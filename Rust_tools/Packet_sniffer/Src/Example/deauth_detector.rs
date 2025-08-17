use packet_sniffer::capture::PacketSniffer;
use pnet::packet::radiotap::RadiotapPacket;

fn main() {
    let mut sniffer = PacketSniffer::new("wlan0");
    println!("🎧 Escuchando en wlan0... (Ctrl+C para detener)");

    ctrlc::set_handler(move || {
        println!("\n📊 Estadísticas: {:?}", sniffer.stats);
        std::process::exit(0);
    }).expect("Error al configurar Ctrl+C");

    sniffer.start();
}
