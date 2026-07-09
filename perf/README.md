# Testes de performance

Este diretório contém um runner sem dependências externas para executar localmente os três perfis pedidos:

- **load**: teste de carga moderada (`200` requisições, concorrência `20`).
- **stress**: teste com alta concorrência (`1000` requisições, concorrência `100`).
- **benchmark**: medição sequencial para linha de base (`500` requisições, concorrência `1`).

O script `perf/run_all.sh` executa os três perfis para os três alvos:

- `laravel-docker` em `http://127.0.0.1/api/health-check`.
- `zig-native` em `http://127.0.0.1:8080/api/health-check`.
- `zig-docker` em `http://127.0.0.1:8081/api/health-check`.

## 1. Subir Laravel no Docker

```bash
docker compose up -d --build
```

Se precisar usar outra URL para o Laravel, exporte `LARAVEL_DOCKER_URL` antes de rodar os testes.

## 2. Subir Zig nativo

Em um terminal separado:

```bash
cd zig
zig build -Doptimize=ReleaseFast
./zig-out/bin/ms-payment-gateway-zig
```

O Zig nativo escuta na porta `8080`.

## 3. Subir Zig no Docker

Em outro terminal separado:

```bash
docker build -t ms-payment-gateway-zig ./zig
docker run --rm -p 8081:8080 ms-payment-gateway-zig
```

O container Zig expõe a porta interna `8080` na porta local `8081` para não conflitar com o Zig nativo.

## 4. Executar todos os testes localmente

Com Laravel/Docker, Zig nativo e Zig/Docker em execução, rode na raiz do repositório:

```bash
./perf/run_all.sh
```

Esse comando cria/atualiza os seguintes arquivos:

- `perf/results/laravel-docker-load.json`
- `perf/results/laravel-docker-stress.json`
- `perf/results/laravel-docker-benchmark.json`
- `perf/results/zig-native-load.json`
- `perf/results/zig-native-stress.json`
- `perf/results/zig-native-benchmark.json`
- `perf/results/zig-docker-load.json`
- `perf/results/zig-docker-stress.json`
- `perf/results/zig-docker-benchmark.json`
- `docs/performance-dashboard.html`

## Executar um teste específico

Também é possível rodar um perfil individual:

```bash
python3 perf/http_perf.py load \
  --target laravel-docker \
  --url http://127.0.0.1/api/health-check \
  --output perf/results/laravel-docker-load.json
```

Troque `load` por `stress` ou `benchmark` conforme necessário.
