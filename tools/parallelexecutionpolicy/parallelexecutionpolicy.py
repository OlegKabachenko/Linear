__all__ = "ParallelExecutionPolicy"


import multiprocessing as mp


class ParallelExecutionPolicy:
    @staticmethod
    def get_process_count(problem_size: int, max_processes: int | None = None) -> int:
        cpu = mp.cpu_count()

        if max_processes is not None:
            cpu = min(cpu, max_processes)

        return min(cpu, problem_size)