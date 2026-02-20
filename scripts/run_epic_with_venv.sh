#!/bin/bash
# 鸣潮帧数据ETL工作流系统 - Epic自动化启动脚本
# 确保使用虚拟环境中的Python和依赖包
# 版本: 1.0
# 创建时间: 2026-02-09

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查虚拟环境
check_venv() {
    if [ ! -d "venv" ]; then
        log_warning "虚拟环境不存在，正在创建..."
        python -m venv venv
        log_success "虚拟环境创建完成"
    fi

    # 激活虚拟环境
    if [ -f "venv/Scripts/activate" ]; then
        # Windows
        source venv/Scripts/activate
    elif [ -f "venv/bin/activate" ]; then
        # Linux/macOS
        source venv/bin/activate
    else
        log_error "无法找到虚拟环境激活脚本"
        exit 1
    fi

    log_success "虚拟环境已激活"
    log_info "Python路径: $(which python)"
    log_info "Python版本: $(python --version)"
}

# 安装依赖
install_dependencies() {
    log_info "检查并安装依赖包..."

    # 升级pip
    python -m pip install --upgrade pip

    # 安装项目依赖
    if [ -f "requirements.txt" ]; then
        # 处理编码问题 - 使用--no-deps避免依赖解析错误
        python -m pip install --no-deps -r requirements.txt || {
            log_warning "使用完整依赖安装失败，尝试单独安装关键包..."
            python -m pip install --no-deps requests>=2.31.0 tqdm>=4.66.0 basedpyright>=1.1.0 ruff>=0.1.0 pytest>=7.0.0 duckdb PyYAML loguru
        }
    else
        log_warning "requirements.txt 不存在，安装核心依赖..."
        python -m pip install requests>=2.31.0 tqdm>=4.66.0 basedpyright>=1.1.0 ruff>=0.1.0 pytest>=7.0.0 duckdb PyYAML loguru
    fi

    log_success "依赖安装完成"

    # 验证安装
    log_info "验证关键依赖包..."
    python -m pip list | grep -E "(requests|tqdm|basedpyright|ruff|pytest|duckdb)" || log_warning "某些包可能未正确安装"
}

# 运行Epic自动化
run_epic() {
    local epic_file=$1
    local verbose=$2

    if [ -z "$epic_file" ]; then
        log_error "请提供Epic文件路径"
        echo "用法: $0 <epic-file> [--verbose]"
        exit 1
    fi

    if [ ! -f "$epic_file" ]; then
        log_error "Epic文件不存在: $epic_file"
        exit 1
    fi

    log_info "开始运行Epic自动化..."
    log_info "Epic文件: $epic_file"

    # 构建命令
    local cmd="python -m autoBMAD.epic_automation.epic_driver $epic_file"
    if [ "$verbose" = "--verbose" ] || [ "$verbose" = "-v" ]; then
        cmd="$cmd --verbose"
    fi

    log_info "执行命令: $cmd"

    # 执行
    eval $cmd
}

# 主函数
main() {
    echo "=============================================="
    echo "  鸣潮帧数据ETL工作流系统 - Epic自动化启动器"
    echo "=============================================="
    echo

    # 解析参数
    EPIC_FILE=""
    VERBOSE=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            --verbose|-v)
                VERBOSE="--verbose"
                shift
                ;;
            -h|--help)
                echo "用法: $0 <epic-file> [--verbose]"
                echo
                echo "参数:"
                echo "  epic-file    Epic文档路径"
                echo "  --verbose    详细输出模式"
                echo "  -h, --help   显示帮助信息"
                exit 0
                ;;
            *)
                if [ -z "$EPIC_FILE" ]; then
                    EPIC_FILE=$1
                else
                    log_error "未知参数: $1"
                    exit 1
                fi
                shift
                ;;
        esac
    done

    # 检查和设置虚拟环境
    check_venv

    # 安装依赖
    install_dependencies

    # 运行Epic
    run_epic "$EPIC_FILE" "$VERBOSE"

    log_success "Epic自动化完成！"
}

# 执行主函数
main "$@"
