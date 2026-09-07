// trustcheck.swift — emulate browser TLS trust (Apple SecTrust) for a dev host:port.
// Usage: swift trustcheck.swift 3000
import Foundation
import Security

let port = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "443"
let host = "localhost"

// Minimal TLS via Network.framework is overkill; use OpenSSL-free path:
// call `openssl s_client` for the chain, then evaluate with SecTrust.
func dumpChainPEM() -> [Data] {
    let p = Process()
    p.executableURL = URL(fileURLWithPath: "/usr/bin/openssl")
    p.arguments = ["s_client", "-connect", "\(host):\(port)", "-servername", host, "-showcerts"]
    let inP = Pipe(); let outP = Pipe()
    p.standardInput = inP; p.standardOutput = outP
    try? p.run(); inP.fileHandleForWriting.closeFile()
    let data = outP.fileHandleForReading.readDataToEndOfFile()
    try? p.waitUntilExit()
    let s = String(data: data, encoding: .utf8) ?? ""
    var certs: [Data] = []
    for block in s.components(separatedBy: "-----BEGIN CERTIFICATE-----").dropFirst() {
        if let end = block.range(of: "-----END CERTIFICATE-----") {
            let pem = "-----BEGIN CERTIFICATE-----" + block[..<end.upperBound]
            if let b64start = pem.firstIndex(of: "\n") {
                let b64 = pem[pem.index(after: b64start)...].replacingOccurrences(of: "-----END CERTIFICATE-----", with: "").replacingOccurrences(of: "\n", with: "")
                if let der = Data(base64Encoded: b64) { certs.append(der) }
            }
        }
    }
    return certs
}

let chainPEMs = dumpChainPEM()
guard !chainPEMs.isEmpty else { print("no cert received on port \(port)"); exit(2) }
var certs: [SecCertificate] = []
for der in chainPEMs {
    if let c = SecCertificateCreateWithData(nil, der as CFData) { certs.append(c) }
}
let policy = SecPolicyCreateSSL(true, host as CFString)
var trust: SecTrust?
let status = SecTrustCreateWithCertificates(certs as CFArray, policy, &trust)
guard status == errSecSuccess, let trust = trust else { print("create trust failed: \(status)"); exit(2) }
if certs.count > 1 {
    // anchor candidates: the CA we serve in the chain
    SecTrustSetAnchorCertificates(trust, Array(certs.dropFirst()) as CFArray)
    SecTrustSetAnchorCertificatesOnly(trust, false)
}
var error: CFError?
let ok = SecTrustEvaluateWithError(trust, &error)
if ok {
    print("SecTrust (browser trust): localhost:\(port) => TRUSTED")
    exit(0)
} else {
    print("SecTrust (browser trust): localhost:\(port) => NOT TRUSTED: \((error as? NSError)?.localizedDescription ?? "?")")
    exit(1)
}
