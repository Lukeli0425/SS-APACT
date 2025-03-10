import numpy as np
import torch
import torch.nn.functional as F
from torch import Tensor
from torch.nn import Module


def pad_double(img:Tensor) -> Tensor:
	"""Pad the images to double of its size (on the last two dimensions).

	Args:
		img (Tensor): Input image tensor.

	Returns:
		Tensor: Padded image tensor.
	"""
	H, W = img.shape[-2:]
	return F.pad(img, (W//2, W//2, H//2, H//2))


def crop_half(img:Tensor) -> Tensor:
	"""Crop images to half of its size (on the last two dimensions).

	Args:
		img (Tensor): Input image tensor.

	Returns:
		Tensor: Cropped image tensor.
	"""
	H, W = img.shape[-2:]
	return img[...,H//4:3*H//4, W//4:3*W//4]


def get_fourier_coord(N:int=80, l:float=3.2e-3, device:str='cuda:0') -> tuple:
	"""Calculate the 2D Fourier space polar coordinates for a given grid size.

	Args:
		N (int, optional): Grid size [pixels]. Defaults to `80`.
		l (float, optional): Grid length [m]. Defaults to `3.2e-3`.
		device (str, optional): Device of the coordinate tensors. Defaults to `'cuda:0'`.

	Returns:
		tuple: 2D Fourier space polar coordinates `[k2D, theta2D]`.
	"""
	fx1D = torch.linspace(-np.pi/l, np.pi/l, N, requires_grad=False, device=device)
	fy1D = torch.linspace(-np.pi/l, np.pi/l, N, requires_grad=False, device=device)
	[fx2D, fy2D] = torch.meshgrid(fx1D, fy1D, indexing='xy')
	k2D = torch.sqrt(fx2D**2 + fy2D**2) * N
	theta2D = torch.arctan2(fy2D, fx2D) + np.pi/2 # Add `np.pi/2` to match the polar definition of the theta.
	return k2D, theta2D % (2*torch.pi)


def get_mgrid(shape:tuple, range:tuple=(-1, 1)) -> Tensor:
    """Generates a flattened grid of (x,y,...) coordinates in a range of `[-1, 1]`.
    
    Args:
        shape (tuple): Shape of the datacude to be fitted.
        range (tuple, optional): Range of the grid. Defaults to `(-1, 1)`.

    Returns:
        Tensor: Generated flattened grid of coordinates.
    """
    tensors = [torch.linspace(range[0], range[1], steps=N) for N in shape]
    mgrid = torch.stack(torch.meshgrid(*tensors, indexing='xy'), dim=-1)
    mgrid = mgrid.reshape(-1, len(shape))
    return mgrid


def get_total_params(model:Module) -> int:
    """Calculate the total number of parameters in a model.
	
	Args:
		model (Module): PyTorch module.

	Returns:
		int: Total number of parameters in the model.
	"""
    return sum([param.nelement() if param.requires_grad else 0 for param in model.parameters()])
