use pnet::datalink::{self, Channel::Ethernet};
use pnet::packet::ethernet::{EthernetPacket, EtherTypes};
use pnet::packet::ip::IpNextHeaderProtocols;
use pnet::packet::tcp::TcpPacket;
use std::collections::HashMap;

pub struct PacketSniffer {
    pub interface: String,
    pub stats: HashMap<String, usize>,
}

impl PacketSniffer {
    pub fn new(interface: &str) -> Self {
        PacketSniffer {
            interface: interface.to_string(),
            stats: HashMap::new(),
        }
    }

    pub fn start(&mut self) {
        let interface = datalink::interfaces()
            .into_iter()
            .find(|iface| iface.name == self.interface)
            .expect("Interface no encontrada");

        let (_, mut rx) = match datalink::channel(&interface, Default::default()) {
            Ok(Ethernet(tx, rx)) => (tx, rx),
            _ => panic!("Error al crear canal Ethernet"),
        };

        loop {
            match rx.next() {
                Ok(packet) => {
                    if let Some(ethernet) = EthernetPacket::new(packet) {
                        self.process_packet(&ethernet);
                    }
                }
                Err(e) => eprintln!("Error: {}", e),
            }
        }
    }

    fn process_packet(&mut self, ethernet: &EthernetPacket) {
        match ethernet.get_ethertype() {
            EtherTypes::Ipv4 => {
                *self.stats.entry("IPv4".to_string()).or_insert(0) += 1;
            }
            EtherTypes::Arp => {
                *self.stats.entry("ARP".to_string()).or_insert(0) += 1;
            }
            _ => {}
        }
    }
}
