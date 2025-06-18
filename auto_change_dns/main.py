import time

from .base_system.context import GlobalContext
from .network_system.while_ping import WhilePing
from .network_system.change_dns import AliyunDNSUpdater


def main():
    """主函数入口"""
    cfg = GlobalContext.get_config()
    logger = GlobalContext.get_logger()

    if cfg.server_ip == "127.0.0.1":
        logger.info("请根据注释修改config.yml内的配置项后再启动程序！")
        return

    # 3. 初始化监控与 DNS 更新模块
    pinger = WhilePing()
    dns_updater = AliyunDNSUpdater(
        cfg.ali_access_key_id,
        cfg.ali_access_key_secret
    )

    # 4. 当前DNS状态（True=已切换到 failover_ip，False=指向 server_ip）
    switched = False

    # 5. 循环监控
    while True:
        rate = pinger.ping_loss_rate(
            host=cfg.server_ip,
            interval=1.0,
            window=cfg.check_time
        )
        logger.info(f"Current loss rate: {rate:.2f}%")

        if rate >= cfg.failover_threshold and not switched:
            # 触发故障切换
            logger.warning("Loss rate exceeded threshold; switching DNS → failover_ip")
            dns_updater.set_dns(
                domain=cfg.domain,
                rr=cfg.rr,
                record_type=cfg.record_type,
                value=cfg.failover_ip,
                ttl=cfg.ttl
            )
            if cfg.rr == "*":
                dns_updater.set_dns(
                    domain=cfg.domain,
                    rr="@",
                    record_type=cfg.record_type,
                    value=cfg.failover_ip,
                    ttl=cfg.ttl
                )
                logger.info("Also updated root record (@) to failover_ip")
            switched = True
            logger.info("DNS updated to failover_ip")

        elif rate < cfg.failover_threshold and switched:
            # 恢复主线路
            logger.warning("Loss rate recovered; switching DNS → server_ip")
            dns_updater.set_dns(
                domain=cfg.domain,
                rr=cfg.rr,
                record_type=cfg.record_type,
                value=cfg.server_ip,
                ttl=cfg.ttl
            )
            if cfg.rr == "*":
                dns_updater.set_dns(
                    domain=cfg.domain,
                    rr="@",
                    record_type=cfg.record_type,
                    value=cfg.server_ip,
                    ttl=cfg.ttl,
                )
                logger.info("Also updated root record (@) to failover_ip")
            switched = False
            logger.info("DNS reverted to server_ip")

        time.sleep(cfg.check_time)
