# -*- coding:utf-8 -*-


class APSchedulerStatus:
    Stop = 0
    Start = 1
    Pause = 2


class ShopType:
    Regular = 1
    Contract = 2
    Agent = 3
    Subagent = 4
    System = 5

    AccessedStatuses = {
        "1": "Regular",
        "2": "Contract",
        "3": "Agent",
        "4": "Subagent",
    }