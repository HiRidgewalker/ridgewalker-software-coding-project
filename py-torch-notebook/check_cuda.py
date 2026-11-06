import torch

def check_cuda_and_cudnn():
    """
    检查CUDA和cuDNN的安装状态
    """
    print("=" * 50)
    print("PyTorch CUDA和cuDNN检查工具")
    print("=" * 50)

    # 检查PyTorch版本
    print(f"PyTorch版本: {torch.__version__}")
    print()

    # 检查CUDA是否可用
    cuda_available = torch.cuda.is_available()
    print(f"CUDA是否可用: {'是' if cuda_available else '否'}")

    if not cuda_available:
        print("\n注意: CUDA不可用，可能的原因:")
        print("1. 未安装NVIDIA显卡驱动")
        print("2. 未安装CUDA Toolkit")
        print("3. 安装的PyTorch版本不支持CUDA")
        print("4. 系统没有NVIDIA GPU")
        return

    # 如果CUDA可用，显示详细信息
    print(f"CUDA版本: {torch.version.cuda}")
    print(f"GPU数量: {torch.cuda.device_count()}")

    # 显示每个GPU的信息
    for i in range(torch.cuda.device_count()):
        print(f"\nGPU {i}:")
        print(f"  名称: {torch.cuda.get_device_name(i)}")
        print(f"  计算能力: {torch.cuda.get_device_capability(i)}")
        print(f"  内存总量: {torch.cuda.get_device_properties(i).total_memory / 1024**3:.2f} GB")

    # 检查cuDNN
    print(f"\ncuDNN版本: {torch.backends.cudnn.version()}")
    print(f"cuDNN是否可用: {'是' if torch.backends.cudnn.is_available() else '否'}")

    if torch.backends.cudnn.is_available():
        print(f"cuDNN enabled: {torch.backends.cudnn.enabled}")

    # 测试简单的CUDA操作
    print("\n测试CUDA操作:")
    try:
        # 创建一个张量并移动到GPU
        x = torch.randn(3, 3)
        print(f"CPU张量创建成功: {x.shape}")

        # 尝试移动到GPU
        if torch.cuda.is_available():
            x_gpu = x.cuda()
            print(f"GPU张量创建成功: {x_gpu.shape}, 设备: {x_gpu.device}")

            # 执行简单操作
            y = torch.randn(3, 3).cuda()
            z = x_gpu + y
            print(f"GPU计算成功: 结果形状 {z.shape}")

            # 如果cuDNN可用，测试深度学习操作
            if torch.backends.cudnn.is_available():
                print("\n测试cuDNN加速的深度学习操作:")
                # 创建一个简单的卷积层来测试cuDNN
                conv = torch.nn.Conv2d(3, 16, 3, padding=1).cuda()
                input_tensor = torch.randn(1, 3, 32, 32).cuda()
                output = conv(input_tensor)
                print(f"卷积操作成功: 输入 {input_tensor.shape} -> 输出 {output.shape}")

    except Exception as e:
        print(f"测试过程中出现错误: {e}")

    print("\n" + "=" * 50)
    print("检查完成!")
    print("=" * 50)

if __name__ == "__main__":
    check_cuda_and_cudnn()