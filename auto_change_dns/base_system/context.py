from logging import Logger
from .log_system import LogSystem
from .storage_system import BaseConfig, ConfigError, Field

class Config(BaseConfig):
    """配置类，继承自BaseConfig"""
    server_ip: str = Field(default="127.0.0.1", description="服务器IP地址")
    check_time: int = Field(default=60, description="检查时间间隔（秒）")
    failover_threshold: int = Field(default=10, description="故障转移阈值（%）")
    failover_ip: str = Field(default="127.0.0.1", description="故障转移IP地址")

    domain: str = Field(default="example.com", description="域名")
    rr: str = Field(default="www", description="记录名称（RR）")
    record_type: str = Field(default="A", description="记录类型")
    ttl: int = Field(default=600, description="TTL（秒）")

    ali_access_key_id: str = Field(default="", description="阿里云Access Key ID")
    ali_access_key_secret: str = Field(default="", description="阿里云Access Key Secret")



class GlobalContext(object):
    def __init__(self, debug: bool, config: BaseConfig = Config):
        """创建公用Context"""
        global _log_system, _config
        _log_system = LogSystem(debug=debug)
        try:
            _config = config.load()
        except ConfigError as e:
            _log_system.logger.error(f"配置操作失败: {str(e)}")

    @staticmethod
    def get_logger() -> Logger:
        """获取logger"""
        return _log_system.logger

    @staticmethod
    def get_log_system() -> LogSystem:
        """获取log_system"""
        return _log_system

    @staticmethod
    def get_config() -> Config:
        """获取Config"""
        return _config
