FROM alpine:3.20 AS build
RUN apk add --no-cache zig
WORKDIR /src
COPY build.zig ./
COPY src ./src
RUN zig build -Doptimize=ReleaseFast

FROM alpine:3.20
COPY --from=build /src/zig-out/bin/ms-payment-gateway-zig /usr/local/bin/ms-payment-gateway-zig
EXPOSE 8080
CMD ["ms-payment-gateway-zig"]
