class EnmpManager:
    @staticmethod
    def dumpEnmpData(enmplist):
        # Every enmp entry is u16
        entries = [
            "id",
            "level",
            "health",
            "maxDamage",
            "minDamage",
            "physicalWeakness",
            "fireWeakness",
            "iceWeakness",
            "thunderWeakness",
            "darkWeakness",
            "lightWeakness",
            "generalWeakness",
            "experience",
            "prize",
            "bonusLevel"
        ]
        def _toBytes(n):
            return n.to_bytes(2, "little")
        header = [2, 0, 0, 0, 229, 0, 0, 0] #taken from vanilla file
        enmp_bytes = bytearray(header)
        for enemy in enmplist:
            for k in entries:
                if k == "health":
                    for healthentry in enemy[k]:
                        enmp_bytes += _toBytes(healthentry)
                    continue
                enmp_bytes += _toBytes(enemy[k])
        return bytes(enmp_bytes)