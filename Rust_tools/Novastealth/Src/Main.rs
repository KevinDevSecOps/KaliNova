use std::process::Command;

fn main() {
    println!("🔥 NovaStealth VPN Activada");
    
    // Ejemplo: Rotación de IP con OpenVPN
    Command::new("sudo")
        .args(&["openvpn", "--config", "/etc/nova/jp.ovpn"])
        .spawn()
        .expect("❌ Error al iniciar VPN");
}
