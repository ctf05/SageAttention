import torch
from flash_attn.utils.benchmark import benchmark_forward
from flash_attn_interface import flash_attn_func as flash_attn_func_v3

import argparse

parser = argparse.ArgumentParser(description='Benchmark FlashAttention3-FP8')
parser.add_argument('--batch_size', type=int, default=4, help='Batch size')
parser.add_argument('--num_heads', type=int, default=32, help='Number of heads')
parser.add_argument('--head_dim', type=int, default=128, help='Head dimension')
args = parser.parse_args()

head = args.num_heads
batch = args.batch_size
headdim = args.head_dim

print(f"FlashAttention3-FP8 Benchmark")
print(f"batch: {batch}, head: {head}, headdim: {headdim}")

is_causal = False
print(f"is_causal: {is_causal}")
for seq_len in {1024, 2048, 4096, 8192, 16384, 32768}:
    flops = 4 * head * batch * headdim * seq_len * seq_len // (2 if is_causal else 1)
    q = torch.randn(batch, seq_len, head, headdim, dtype=torch.float16, device="cuda").to(torch.float8_e4m3fn)
    k = torch.randn(batch, seq_len, head, headdim, dtype=torch.float16, device="cuda").to(torch.float8_e4m3fn)
    v = torch.randn(batch, seq_len, head, headdim, dtype=torch.float16, device="cuda").to(torch.float8_e4m3fn)
    descale_q = torch.tensor([1.0], dtype=torch.float32, device="cuda")
    descale_k = torch.tensor([1.0], dtype=torch.float32, device="cuda")
    descale_v = torch.tensor([1.0], dtype=torch.float32, device="cuda")
    for i in range(5): flash_attn_func_v3(q, k, v, 1 / headdim**0.5, causal=is_causal, descale_q=descale_q, descale_k=descale_k, descale_v=descale_v)
    torch.cuda.synchronize()
    _, time = benchmark_forward(flash_attn_func_v3, q, k, v, 1 / headdim**0.5, causal=is_causal,descale_q=descale_q, descale_k=descale_k, descale_v=descale_v, repeats=100, verbose=False, desc='Triton')
    print(f'{seq_len} flops:{flops/time.mean*1e-12}')

is_causal = True
print(f"is_causal: {is_causal}")
for seq_len in {1024, 2048, 4096, 8192, 16384, 32768}:
    flops = 4 * head * batch * headdim * seq_len * seq_len // (2 if is_causal else 1)
    q = torch.randn(batch, seq_len, head, headdim, dtype=torch.float16, device="cuda").to(torch.float8_e4m3fn)
    k = torch.randn(batch, seq_len, head, headdim, dtype=torch.float16, device="cuda").to(torch.float8_e4m3fn)
    v = torch.randn(batch, seq_len, head, headdim, dtype=torch.float16, device="cuda").to(torch.float8_e4m3fn)
    descale_q = torch.tensor([1.0], dtype=torch.float32, device="cuda")
    descale_k = torch.tensor([1.0], dtype=torch.float32, device="cuda")
    descale_v = torch.tensor([1.0], dtype=torch.float32, device="cuda")
    for i in range(5): flash_attn_func_v3(q, k, v, 1 / headdim**0.5, causal=is_causal, descale_q=descale_q, descale_k=descale_k, descale_v=descale_v)
    torch.cuda.synchronize()
    _, time = benchmark_forward(flash_attn_func_v3, q, k, v, 1 / headdim**0.5, causal=is_causal,descale_q=descale_q, descale_k=descale_k, descale_v=descale_v, repeats=100, verbose=False, desc='Triton')
    print(f'{seq_len} flops:{flops/time.mean*1e-12}')