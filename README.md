# CSEE4119 Project1

[Project Description - preliminary stage](https://docs.google.com/document/d/18YFVuQHE5dwW3Ue5-ktfpa5MmVE0ax4YKQr-tbDAwsY/edit#heading=h.k7og163d2a56)

[Project Description - final stage](https://docs.google.com/document/d/1anqMmGCMh6pzcxaMjMBWdeaXXtU62feKaL488p27mn0/edit#heading=h.k7og163d2a56)

## Links

### Google Cloud

<https://console.cloud.google.com/>

### Chrome Remote Desktop

<https://remotedesktop.google.com/access/>

## Test inputs

```bash
# proxy.py: topo_dir, log_path, alpha, listen_port, fake_ip, dns_server_port
python proxy.py ../topos/topo1 proxy1_log.txt 0.5 8011 127.0.0.1 53

# dns_server.py: topo_dir, log_path, listen_port, decision_method
python dns_server.py ../topos/topo1 dns_log.txt 53 round-robin

# dig
dig @localhost video.columbia.edu
```