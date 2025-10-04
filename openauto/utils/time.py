from PyQt6 import QtCore
import datetime as _dt

def to_qdatetime(dt) -> QtCore.QDateTime:
    if isinstance(dt, _dt.datetime):
        return QtCore.QDateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    if isinstance(dt, str) and dt:
        ts = dt.split('.')[0]
        qdt = QtCore.QDateTime.fromString(ts, "yyyy-MM-dd HH:mm:ss")
        if qdt.isValid(): return qdt
    return QtCore.QDateTime()
