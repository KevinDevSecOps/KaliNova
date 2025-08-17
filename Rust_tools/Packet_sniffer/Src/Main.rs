use clap::Parser;
use pnet::datalink;
use std::process;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;

// Configuración desde CLI
#[derive(Parser)]
#[command(name = "NovaSniffer")]
#[command(version = "1.0")]
#[command(about = "Packet sniffer de alto rendimiento para KaliNova", long_about = None)]
struct Args {
    /// Interfaz de red a escuchar (ej: wlan0, eth0)
    #[arg(short, long, default_value = "wlan0")]
    interface: String,

    /// Modo verbose (muestra todo el tráfico)
    #[arg(short, long, action)]
    verbose: bool,

    /// Filtro de protocolo (arp, tcp, udp, etc)
    #[arg(short, long, default_value = "all")]
    filter: String,
}

fn main() {
    let args = Args::parse();
    
    // Configurar Ctrl+C
    let running = Arc::new(AtomicBool::new(true));
    let r = running.clone();
    
    ctrlc::set_handler(move || {
        r.store(false, Ordering::SeqCst);
        println!("\n🛑 Deteniendo el sniffer...");
    }).expect("Error al configurar Ctrl+C");

    // Validar interfaz
    let interfaces = datalink::interfaces();
    let interface = interfaces.iter()
        .find(|iface| iface.name == args.interface)
        .unwrap_or_else(|| {
            eprintln!("❌ Interfaz {} no encontrada", args.interface);
            process::exit(1);
        });

    println!("🎧 Escuchando en {} (Filtro: {})", interface.name, args.filter);
    println!("📊 Presiona Ctrl+C para detener y ver estadísticas\n");

    // Iniciar captura
    let mut sniffer = PacketSniffer::new(&interface.name);
    while running.load(Ordering::SeqCst) {
        if let Err(e) = sniffer.capture_packet(&args.filter, args.verbose) {
            eprintln!("⚠️ Error: {}", e);
        }
    }

    // Mostrar estadísticas al finalizar
    println!("\n--- Resumen ---");
    for (proto, count) in &sniffer.stats {
        println!("🔹 {}: {} paquetes", proto, count);
    }
}
