import time
from concurrent import futures
from threading import Event, Thread

import grpc
import rideMetrics_pb2 as pb2
import rideMetrics_pb2_grpc as pb2_grpc
from RideMetrics import main, testStatusEnum

testStatus = None

# Set event
event = Event()


class RideMetric(pb2_grpc.RideMetricServicer):
    def pollTestStatus(self, request, context):
        from RideMetrics import testExecutionStatus

        global testStatus
        testStatus = request.startTest
        return pb2.testResponse(
            testStarted=testExecutionStatus.name, testStatus=testStatus
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_RideMetricServicer_to_server(RideMetric(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    print("Running GRPC server")
    th = Thread(target=serve)
    th.start()

    # Only create new thread if the variable is False
    THREAD_ALIVE = False

    while True:
        print("Waiting for GRPC request...")
        time.sleep(2)

        if testStatus == "START":
            if THREAD_ALIVE == False:
                main_fn_th = Thread(target=main, args=(event,), name="Processor_thread")
                main_fn_th.start()
                THREAD_ALIVE = True
            testExecutionStatus = testStatusEnum.DEFAULT
            time.sleep(5)

        # Pause the thread
        elif testStatus == "PAUSE":
            print("Event paused")
            event.set()

        elif testStatus == "RESUME":
            print("Event resumed")
            event.clear()

        elif testStatus == "EXIT":
            main_fn_th.join()
            THREAD_ALIVE = False
            print("Processor thread killed. Server thread alive")
