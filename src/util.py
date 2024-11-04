from pathlib import Path


def generate_metrics(perm, head_cont, cycles, tot_ins, io_dir: Path):
    file_path = io_dir / "PerformanceMetrics_Result.txt"

    content = [head_cont + "\n",
               f"Number of cycles taken: {cycles}\n",
               f"Cycles per instruction: {(cycles / tot_ins):.6}\n",
               f"Instructions per cycle: {(tot_ins / cycles):.6}\n\n"]

    with open(file_path, perm) as wf:
        wf.writelines(content)