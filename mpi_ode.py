from mpi4py import MPI
from mpi_master_slave import Master, Slave
from mpi_master_slave import WorkQueue
import time
from assimulo.solvers import CVode
from assimulo.problem import Explicit_Problem
import numpy as np


def py_rhs_fun(t, y, p):
    alpha = p[0]
    beta = p[1]
    delta = p[2]
    gamma = p[3]

    flux = np.array([alpha * y[0], beta * y[0] * y[1], delta * y[0] * y[1], gamma * y[1]])
    rhs = np.array([flux[0] - flux[1], flux[2] - flux[3]])

    return rhs


class MyApp(object):
    """
    This is my application that has a lot of work to do so it gives work to do
    to its slaves until all the work is done. There different type of work so
    the slaves must be able to do different tasks
    """

    def __init__(self, slaves):
        # when creating the Master we tell it what slaves it can handle
        self.master = Master(slaves)
        # WorkQueue is a convenient class that run slaves on a tasks queue
        self.work_queue = WorkQueue(self.master)

    def terminate_slaves(self):
        """
        Call this to make all slaves exit their run loop
        """
        self.master.terminate_slaves()

    def __add_next_task(self, i, p, task=()):
        """
        we create random tasks 1-3 and add it to the work queue
        Every task has specific arguments
        """
        # if task:
        # set ode rhs function
        data = {'ode_fun': py_rhs_fun, 'y0': task, 'y0_id': i, 'p': p}
        # else:
        #     data = {'ode_fun': None, 'y0': None}
        # if task is None:
        #     task = random.randint(1, 3)
        #
        # if task == 1:
        #     args = i
        #     data = (Tasks.TASK1, args)
        # elif task == 2:
        #     args = (i, i * 2)
        #     data = (Tasks.TASK2, args)
        # elif task == 3:
        #     args = (i, 999, 'something')
        #     data = (Tasks.TASK3, args)

        self.work_queue.add_work(data)

    def run(self, tasks=[]):
        """
        This is the core of my application, keep starting slaves
        as long as there is work to do
        """
        # set parameter value
        p = np.array([.5, .02, .4, .004])

        # let's prepare our work queue. This can be built at initialization time
        # but it can also be added later as more work become available
        #
        for idx, i_y0 in enumerate(tasks):
            self.__add_next_task(idx, p, task=i_y0)

        #
        # Keeep starting slaves as long as there is work to do
        #
        while not self.work_queue.done():

            #
            # give more work to do to each idle slave (if any)
            #
            self.work_queue.do_work()

            #
            # reclaim returned data from completed slaves
            #
            for slave_return_data in self.work_queue.get_completed_work():
                import pdb; pdb.set_trace()
                tout, yout, y0_id = slave_return_data
                #
                # each task type has its own return type
                #
                # task, data = slave_return_data
                # if task == Tasks.TASK1:
                #     done, arg1 = data
                # elif task == Tasks.TASK2:
                #     done, arg1, arg2, arg3 = data
                # elif task == Tasks.TASK3:
                #     done, arg1, arg2 = data
                # if done:
                print('Master: slave finished its task returning: %s)' % str(y0_id))

            # sleep some time
            time.sleep(0.3)


class MySlave(Slave):
    """
    A slave process extends Slave class, overrides the 'do_work' method
    and calls 'Slave.run'. The Master will do the rest
    In this example we have different tasks but instead of creating a Slave for
    each type of taks we create only one class that can handle any type of work.
    This avoids having idle processes if, at certain times of the execution, there
    is only a particular type of work to do but the Master doesn't have the right
    slave for that task.
    """

    def __init__(self):
        super(MySlave, self).__init__()

    def do_work(self, data):

        # the data contains the task type
        # task, data = args
        # define explicit assimulo problem
        import pdb; pdb.set_trace()
        rhs_fun = data['ode_fun']
        y_initial = data['y0']
        y0_id = data['y0_id']
        p = data['p']
        prob = Explicit_Problem(lambda t, x: rhs_fun(t, x, p), y0=y_initial)

        # create solver instance
        solver = CVode(prob)

        solver.iter = 'Newton'
        solver.discr = 'Adams'
        solver.atol = 1e-10
        solver.rtol = 1e-10
        solver.display_progress = True
        solver.verbosity = 30

        rank = MPI.COMM_WORLD.Get_rank()
        name = MPI.Get_processor_name()

        #
        # Every task type has its specific data input and return output
        #
        # ret = None
        # if task == Tasks.TASK1:
        #
        #     arg1 = data
        #     print('  Slave %s rank %d executing %s with task_id %d' % (name, rank, task, arg1))
        #     ret = (True, arg1)
        #
        # elif task == Tasks.TASK2:
        #
        #     arg1, arg2 = data
        print('  Slave %s rank %d executing %s with task_id %d' % (name, rank, y0_id, y_initial))
        #     ret = (True, arg1, 'something', 'else')
        #
        # elif task == Tasks.TASK3:
        #
        #     arg1, arg2, arg3 = data
        #     print('  Slave %s rank %d executing %s with task_id %d arg2 %d arg3 %s' % (
        #     name, rank, task, arg1, arg2, arg3))
        #     ret = (True, arg1, 'something')
        # simulate system
        time_course, y_result = solver.simulate(10, 200)

        return time_course, y_result, y0_id


if __name__ == "__main__":
    name = MPI.Get_processor_name()
    rank = MPI.COMM_WORLD.Get_rank()
    size = MPI.COMM_WORLD.Get_size()

    print('I am  %s rank %d (total %d)' % (name, rank, size))

    if rank == 0:  # Master
        import pdb; pdb.set_trace()
        y0 = [np.array([1, .0001]), np.array([2, .0001]), np.array([3, .0001]), np.array([4, .0001]),
              np.array([5, .0001]), np.array([.0001, 1]), np.array([.0001, 2]), np.array([.0001, 3]),
              np.array([.0001, 4]), np.array([.0001, 5]), np.array([10, 1]), np.array([1, 10])]
        import pdb; pdb.set_trace()
        app = MyApp(slaves=range(1, size))
        import pdb; pdb.set_trace()
        app.run(tasks=y0)
        app.terminate_slaves()

    else:  # Any slave

        MySlave().run()

    print('Task completed (rank %d)' % (rank))
