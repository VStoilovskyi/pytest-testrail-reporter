import pickle

from pytest_testrail_integrator.client import TrClient, WORKER_RESULTS_KEY


class XdistTrClintAdapter:
    def __init__(self, tr_client: TrClient):
        self._tr_client = tr_client

    def pytest_testnodedown(self, node, error):
        """Extend master node results with worker's node results."""
        node_reports = pickle.loads(node.workeroutput[WORKER_RESULTS_KEY])
        self._tr_client.add_results(node_reports)
