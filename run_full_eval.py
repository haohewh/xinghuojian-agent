import sys, json, asyncio, time
sys.path.insert(0, "/opt/myapp")
from core.starpivot.registry import ToolRegistry
from core.starpivot.engine import StarPivotEngine
from core.starpivot.spark.judge import SparkJudge, WEIGHTS

reg = ToolRegistry()
cnt = reg.discover_servers("/opt/myapp/mcp_servers")
tools = reg.list_tools()
print(f"发现 {cnt} 个 MCP Server, {len(tools)} 个工具")
print()

order = sorted(WEIGHTS.items(), key=lambda x: -x[1])
print("星火鉴最终权重:")
for k, v in order:
    print(f"  {k}: {int(v*100)}%")
print()

engine = StarPivotEngine(reg)
judge = SparkJudge(engine=engine, registry=reg)

headers = ["工具名","实用","稳定","兼容","时速","安全","好评","更新","革命","工业","总分","等级"]
print(" | ".join(f"{h:>5}" for h in headers))
print("-" * 90)

for t in tools[:15]:
    # 重置熔断器，避免前一个测试的熔断影响当前工具
    try:
        cb = getattr(judge._engine, '_circuit_breaker', None)
        if cb and hasattr(cb, '_failures'):
            cb._failures.clear()
            cb._open_until.clear()
    except:
        pass
    try:
        r = asyncio.run(judge.evaluate(t.name, save_to_db=False))
        vals = [t.name[:20],
                str(int(r["utility"])),
                str(int(r["stability"])),
                str(int(r["compatibility"])),
                str(int(r["speed"])),
                str(int(r["security"])),
                str(int(r["review"])),
                str(int(r["update"])),
                str(int(r["revolution"])),
                str(int(r["industrial"])),
                f'{r["total"]:.1f}',
                r["grade"]]
        print(" | ".join(f"{v:>5}" for v in vals))
    except Exception as e:
        print(f"{t.name[:20]:20s} | 错误: {str(e)[:40]}")

asyncio.run(engine.close())
print("\n测评完成")
