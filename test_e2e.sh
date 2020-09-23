#!/bin/bash

set -e

wait_var_nonzero () {
	var=$1
	query="http://0.0.0.0:9090/api/v1/query?query=$var>0"
	echo waiting for $query to be non-zero
        RC="[]"
        TRIES=0
        while [[ "$RC" == "[]" ]] || [[ $RC == "" ]] ; do
                RC=$(echo "$query" | wget -q -O- -i -|jq .data.result)
                sleep 1
                TRIES=$((TRIES+1))
                if [[ "$TRIES" == "30" ]] ; then
			echo $query timed out: $RC
                        exit 1
                fi
        done
}

wait_job_up () {
	instance=$1
	wait_var_nonzero "up{instance=\"$instance\"}"
}

# TODO: push test capture into switch1:1 to ensure networkml is called
sudo rm -rf /etc/faucet
sudo mkdir -p /etc/faucet
cat >/tmp/faucet.yaml<<EOF
# compatible with default poseidon config.
dps:
  switch1:
    dp_id: 0x999
    hardware: Open vSwitch
    interfaces:
        1:
           native_vlan: 100
        3:
           output_only: true
EOF
sudo mv /tmp/faucet.yaml /etc/faucet

docker-compose -f test-e2e-ovs.yml down
docker-compose -f test-e2e-ovs.yml rm -f
docker-compose -f test-e2e-ovs.yml up -d
OVSID="$(docker ps -q --filter name=ovs)"
while ! docker exec -t $OVSID ovs-vsctl show ; do
        echo waiting for OVS
        sleep 1
done
sudo sudo ip link add sw1a type veth peer name sw1b && true
sudo sudo ip link add mirrora type veth peer name mirrorb && true
sudo ip link set sw1a up
sudo ip link set sw1b up
sudo ip link set mirrora up
sudo ip link set mirrorb up
docker exec -t $OVSID ovs-vsctl add-br switch1 
docker exec -t $OVSID ovs-vsctl add-port switch1 sw1a -- set interface sw1a ofport_request=1
docker exec -t $OVSID ovs-vsctl add-port switch1 mirrora -- set interface mirrora ofport_request=3
docker exec -t $OVSID ovs-vsctl set-controller switch1 tcp:127.0.0.1:6653,tcp:127.0.0.1:6654
docker exec -t $OVSID ovs-vsctl show
docker exec -t $OVSID ovs-ofctl dump-ports switch1
export POSEIDON_PREFIX=/
export PATH=bin:$PATH
poseidon -i
poseidon -s
wait_job_up faucet:9302
wait_job_up gauge:9303
wait_job_up poseidon:9304
wait_var_nonzero "last_rabbitmq_routing_key_time"
poseidon -a
# TODO: ensure test capture container is learned.
# TODO: provide pty
# poseidon -e "show all"  "quit"
poseidon -S
poseidon -d
docker-compose -f test-e2e-ovs.yml stop