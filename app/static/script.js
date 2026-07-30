//import Chart from 'chart.js';

let blackScholesPrice = null;

async function runPricing() {
  const scenario = document.getElementById("scenario").value;

  let params = {
    S0: parseFloat(document.getElementById("S0").value),
    K: parseFloat(document.getElementById("K").value),
    r: parseFloat(document.getElementById("r").value),
    sigma: parseFloat(document.getElementById("sigma").value),
    T: parseFloat(document.getElementById("T").value),
    n_samples: parseInt(document.getElementById("n").value),
    antithetic: document.getElementById("anti").checked
  };

  if (scenario === "var" || scenario === "correlated_var") {
    console.log("works too");
    delete params.K;
    delete params.antithetic;
  }

  if (scenario === "asian_call") {
    delete params.antithetic;
  }

  if (scenario === "correlated_var") {
    params = {
      S0_1: parseFloat(document.getElementById("S01").value),
      S0_2: parseFloat(document.getElementById("S02").value),
      sigma_1: parseFloat(document.getElementById("sigma").value),
      sigma_2: parseFloat(document.getElementById("sigma").value),
      w1: parseFloat(document.getElementById("w1").value),
      w2: parseFloat(document.getElementById("w2").value),
      r: parseFloat(document.getElementById("r").value),
      T: parseFloat(document.getElementById("T").value),
      rho: parseFloat(document.getElementById("rho").value),
      n_samples: parseInt(document.getElementById("n").value)
    };
  }

  const body = {
    scenario: scenario,
    parameters: params
  };

  const res = await fetch("/simulate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });

  const data = await res.json();
  const result = data.result;

  document.getElementById("price").textContent = "—";
  document.getElementById("se").textContent = "—";
  document.getElementById("ciLow").textContent = "—";
  document.getElementById("ciHigh").textContent = "—";

  if (scenario === "var") {
    document.getElementById("price").textContent =
      result.VaR.toFixed(4);
    document.getElementById("se").textContent =
      `Confidence: ${result.confidence}`;
    return;
  }

  if (scenario === "correlated_var") {
    console.log("works");
    document.getElementById("price").textContent =
      `VaR: ${result.VaR.toFixed(4)}`;
    document.getElementById("se").textContent =
      `Confidence: ${result.confidence}`;
    document.getElementById("ciLow").textContent =
      `Correlation: ${result.correlation.toFixed(4)}`;
    return;
  }

  if (result.black_scholes !== undefined) {
    blackScholesPrice = result.black_scholes;
    document.getElementById("bsPrice").textContent =
      result.black_scholes.toFixed(4);

    document.getElementById("bsError").textContent =
      result.absolute_error.toFixed(4);
  }

  if (result.runtime_ms !== undefined) {
    document.getElementById("runtime").textContent =
      result.runtime_ms.toFixed(2);
  }

  document.getElementById("price").textContent =
    result.price.toFixed(4);

  document.getElementById("se").textContent =
    result.standard_error.toFixed(4);

  document.getElementById("ciLow").textContent =
    result.ci_low.toFixed(4);

  document.getElementById("ciHigh").textContent =
    result.ci_high.toFixed(4);

  updateEducationPanel(scenario);

}

let chart;

async function runSweep() {
  const scenario = document.getElementById("scenario").value;

  let baseParams = {
    S0: parseFloat(S0.value),
    K: parseFloat(K.value),
    r: parseFloat(r.value),
    sigma: parseFloat(sigma.value),
    T: parseFloat(T.value),
    n_samples: parseInt(document.getElementById("n").value),
    antithetic: document.getElementById("anti").checked
  };

  if (scenario === "correlated_var") {
    baseParams = {
      S0_1: parseFloat(document.getElementById("S01").value),
      S0_2: parseFloat(document.getElementById("S02").value),
      sigma_1: parseFloat(document.getElementById("sigma").value),
      sigma_2: parseFloat(document.getElementById("sigma").value),
      w1: parseFloat(document.getElementById("w1").value),
      w2: parseFloat(document.getElementById("w2").value),
      r: parseFloat(document.getElementById("r").value),
      T: parseFloat(document.getElementById("T").value),
      rho: parseFloat(document.getElementById("rho").value),
      n_samples: parseInt(document.getElementById("n").value)
    };
  }

  if (scenario === "var") {
    delete baseParams.K;
    delete baseParams.antithetic;
  }

  if (scenario === "asian_call") {
    delete baseParams.antithetic;
  }

  const body = {
    scenario: scenario,
    parameters: baseParams,
    sample_sizes: [100, 200, 300, 500, 800, 1000, 2000, 5000, 8000, 10000]
  };

  const res = await fetch("/sweep", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });

  const data = await res.json();
  renderChart(data.points, scenario);
}

function renderChart(points, scenario) {
  const ns = points.map(p => p.n);

  let estimates, errors;

  if (scenario === "var") {
    estimates = points.map(p => p.VaR);
    errors = null;
  } else {
    estimates = points.map(p => p.price);
    errors = points.map(p => p.standard_error);
  }

  const datasets = [
    {
      label: "Monte Carlo Estimate",
      data: estimates,
      borderColor: "#38bdf8",
      backgroundColor: "transparent",
      yAxisID: "yEstimate",
      tension: 0.2
    }
  ];

  if (errors) {
    datasets.push({
      label: "Standard Error",
      data: errors,
      borderColor: "#f59e0b",
      backgroundColor: "transparent",
      yAxisID: "yError",
      tension: 0.2
    });
  }

  if (scenario === "european_call" && blackScholesPrice !== null) {
    datasets.push({
      label: "Black–Scholes (Analytical)",
      data: ns.map(() => blackScholesPrice),
      borderColor: "#22c55e",
      borderDash: [6, 6],
      yAxisID: "yEstimate",
      tension: 0
    });
  }

  if (chart) chart.destroy();

  chart = new Chart(document.getElementById("convChart"), {
    type: "line",
    data: {
      labels: ns.map(Number),
      datasets: datasets
    },
    options: {
      responsive: true,
      interaction: {
        mode: "index",
        intersect: false
      },
      scales: {
        x: {
          type: "linear",
          title: {
            display: true,
            text: "Samples (N)"
          }
        },
        yEstimate: {
          type: "linear",
          position: "left",
          title: {
            display: true,
            text: "Estimate"
          }
        },
        yError: {
          type: "linear",
          position: "right",
          grid: {
            drawOnChartArea: false
          },
          title: {
            display: true,
            text: "Standard Error"
          }
        }
      }
    }
  });
}



//window.runPricing = runPricing;
//window.runSweep = runSweep;

function updateEducationPanel(scenario) {
  const panel = document.getElementById("eduContent");

  const content = {
    european_call: `
      <p><b>What is happening?</b><br>
      We simulate many future prices of the stock and compute the payoff
      max(Sₜ − K, 0). The option price is the average discounted payoff.</p>

      <p><b>Why Monte Carlo?</b><br>
      Closed-form formulas fail for complex payoffs. Monte Carlo works universally.</p>

      <p><b>Business use:</b><br>
      Traders compare this price with the market to detect mispricing.</p>
    `,
    asian_call: `
      <p><b>Asian Call Option</b></p>
      <p>
      The payoff depends on the <b>average price</b> over time, not just
      the final price. This reduces volatility and makes manipulation harder.
      </p>
      <p>
      <b>Why Monte Carlo?</b> There is no closed-form solution for most
      Asian options.
      </p>
      <p>
      <b>Business use:</b> Common in commodity and energy markets.
      </p>
    `,
    var: `
      <p><b>What is VaR?</b><br>
      VaR answers: “How much can I lose on a bad day with X% confidence?”</p>

      <p><b>Important:</b><br>
      VaR is NOT the worst loss. It ignores what happens beyond the cutoff.</p>

      <p><b>Business use:</b><br>
      Used by banks to set capital buffers and risk limits.</p>
    `,
    correlated_var: `
      <p><b>Why correlation matters?</b><br>
      During stress, assets move together. Correlation increases tail risk.</p>

      <p><b>Key insight:</b><br>
      Diversification fails when correlation rises.</p>
    `
  };

  panel.innerHTML = content[scenario] || "";
}
