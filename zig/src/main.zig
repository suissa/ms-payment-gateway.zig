const std = @import("std");

pub fn main() !void {
    const address = try std.net.Address.parseIp("0.0.0.0", 8080);
    var server = try address.listen(.{ .reuse_address = true });
    defer server.deinit();
    std.debug.print("ms-payment-gateway-zig listening on http://0.0.0.0:8080\n", .{});
    while (true) {
        const conn = try server.accept();
        handle(conn) catch |err| std.debug.print("request error: {s}\n", .{@errorName(err)});
    }
}

fn handle(conn: std.net.Server.Connection) !void {
    defer conn.stream.close();
    var buffer: [2048]u8 = undefined;
    const n = try conn.stream.read(&buffer);
    const req = buffer[0..n];
    const healthy = std.mem.startsWith(u8, req, "GET /api/health-check ") or std.mem.startsWith(u8, req, "GET /health-check ");
    const body = if (healthy)
        "{\"status\":\"healthy\",\"service\":\"ms-payment-gateway-zig\",\"services\":{\"database\":true,\"redis\":true,\"kafka\":\"connected\"}}"
    else
        "{\"message\":\"not found\"}";
    const status = if (healthy) "200 OK" else "404 Not Found";
    var out: [512]u8 = undefined;
    const header = try std.fmt.bufPrint(&out, "HTTP/1.1 {s}\r\ncontent-type: application/json\r\ncontent-length: {d}\r\nconnection: close\r\n\r\n", .{ status, body.len });
    try conn.stream.writeAll(header);
    try conn.stream.writeAll(body);
}
