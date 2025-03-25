import torch
from torch_scatter import scatter_max

print("PyTorch:", torch.__version__)
print("CUDA:", torch.cuda.is_available())
print("CUDA:", torch.version.cuda)

index = torch.tensor([0, 0, 1, 1], device='cuda')
src = torch.tensor([1, 2, 3, 4], device='cuda')
out = scatter_max(src, index, dim=0)
print(out)