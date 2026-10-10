import unittest
import numpy as np
from ccr_engine.risk_metrics import PortfolioRiskEngine

class TestCCRMetrics(   ):
    def setUp(self):
        self.dummy_exposure = np.ones((10, 5)) * 1e6
        self.time_grid = np.linspace(0, 4, 5)
        
        mock_paths = np.zeros((10, 5))
        self.engine = PortfolioRiskEngine(mock_paths, mock_paths, mock_paths, self.time_grid)
        
    def test_current_exposure(self):
        metrics = self.engine.compute_metrics(self.dummy_exposure)
        self.assertEqual(metrics["Current Exposure"], 1e6)
        
    def test_ee_and_pfe_profiles(self):
        metrics = self.engine.compute_metrics(self.dummy_exposure)
        np.testing.assert_array_equal(metrics["EE Profile"], np.ones(5) * 1e6)
        np.testing.assert_array_equal(metrics["PFE Profile"], np.ones(5) * 1e6)
        
    def test_epe_calculation(self):
        metrics = self.engine.compute_metrics(self.dummy_exposure)
        self.assertAlmostEqual(metrics["Expected Positive Exposure (EPE)"], 1e6, places=2)

if __name__ == '__main__':
    unittest.main()