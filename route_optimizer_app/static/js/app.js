document.addEventListener('DOMContentLoaded', function () {
    let evaluation = window.CURRENT_EVALUATION;
    let barChart = null;

    function formatHoursMins(minutes) {
        const totalMins = Math.round(minutes);
        const hrs = Math.floor(totalMins / 60);
        const mins = totalMins % 60;
        if (hrs > 0) {
            return `${hrs}h ${mins < 10 ? '0' + mins : mins}m`;
        }
        return `${mins}m`;
    }

    // 1. Initialize Bar Chart
    const barCtx = document.getElementById('barChart');
    if (barCtx && evaluation && evaluation.routes) {
        initBarChart(evaluation);
    }

    function initBarChart(data) {
        const routeOrder = ["A->C->D", "A->C->E", "B->C->D", "B->C->E"];
        const routeMap = {};
        data.routes.forEach(r => { routeMap[r.route] = r; });

        const labels = routeOrder;
        const durations = labels.map(r => routeMap[r] ? Math.round(routeMap[r].duration_min) : 0);

        const backgroundColors = labels.map(r => {
            return r === data.best_route ? 'rgba(22, 163, 74, 0.85)' : 'rgba(148, 163, 184, 0.7)';
        });

        const borderColors = labels.map(r => {
            return r === data.best_route ? '#15803d' : '#64748b';
        });

        if (barChart) {
            barChart.data.labels = labels;
            barChart.data.datasets[0].data = durations;
            barChart.data.datasets[0].backgroundColor = backgroundColors;
            barChart.data.datasets[0].borderColor = borderColors;
            barChart.update();
            return;
        }

        barChart = new Chart(barCtx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Trip Duration',
                    data: durations,
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 1.5,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 600,
                    easing: 'easeOutQuart'
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const routeName = context.label;
                                const r = routeMap[routeName];
                                let txt = `Duration: ${r ? r.duration_formatted : formatHoursMins(context.parsed.y)}`;
                                if (r && !r.is_best) {
                                    txt += ` (+${r.time_saved_formatted} vs best)`;
                                } else if (r && r.is_best) {
                                    txt += ` (Optimal route)`;
                                }
                                return txt;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 40,
                        title: {
                            display: true,
                            text: 'Trip Duration (hours & minutes)',
                            font: { weight: '600', size: 12 }
                        },
                        ticks: {
                            callback: function (value) {
                                return formatHoursMins(value);
                            },
                            font: { size: 11 }
                        },
                        grid: {
                            color: 'rgba(226, 232, 240, 0.7)'
                        }
                    },
                    x: {
                        grid: { display: false },
                        ticks: {
                            font: { weight: '700', size: 13 }
                        }
                    }
                }
            }
        });
    }

    // 2. Interactive AJAX Optimization with Creative Animation
    const timeForm = document.getElementById('timeForm');
    const optimizeBtn = document.getElementById('optimizeBtn');
    const btnIcon = document.getElementById('btnIcon');
    const btnText = document.getElementById('btnText');
    const hourSelect = document.getElementById('hourSelect');
    const minsInput = document.getElementById('minsInput');
    const recalcNotice = document.getElementById('recalcNotice');

    if (timeForm) {
        timeForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const h = hourSelect.value;
            const m = minsInput.value || "00";
            runOptimization(h, m);
        });
    }

    // Quick selection pills
    document.querySelectorAll('.quick-pill').forEach(pill => {
        pill.addEventListener('click', function (e) {
            e.preventDefault();
            const h = this.getAttribute('data-hour');
            const m = this.getAttribute('data-mins');
            if (h && m) {
                hourSelect.value = h;
                minsInput.value = m;
                runOptimization(h, m);
            }
        });
    });

    async function runOptimization(hour, mins) {
        // Format minute nicely
        let mVal = parseInt(mins, 10);
        if (isNaN(mVal) || mVal < 0) mVal = 0;
        if (mVal > 59) mVal = 59;
        const formattedMin = mVal < 10 ? '0' + mVal : mVal.toString();
        minsInput.value = formattedMin;

        // Animate Button -> Calculating State
        if (optimizeBtn) {
            optimizeBtn.disabled = true;
            btnIcon.className = "bi bi-arrow-repeat spin me-1";
            btnText.textContent = "Calculating...";
        }

        // Apply subtle calculating shimmer to main cards
        const targetCards = ['bestRouteCard', 'savingsCard', 'tableCard', 'chartCard'];
        targetCards.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.classList.add('is-calculating');
        });

        const startTime = Date.now();

        try {
            const resp = await fetch(`/api/predict?hour=${encodeURIComponent(hour)}&minute=${encodeURIComponent(formattedMin)}`);
            if (!resp.ok) {
                const errData = await resp.json();
                throw new Error(errData.error || 'Optimization error');
            }
            const data = await resp.json();

            // Guarantee a minimum 300ms display so the user visibly perceives the calculation
            const elapsed = Date.now() - startTime;
            if (elapsed < 320) {
                await new Promise(r => setTimeout(r, 320 - elapsed));
            }

            // Update DOM with new data
            updateDOMWithResults(data);

            // Update URL without page reload
            window.history.pushState({}, '', `/?hour=${hour}&mins=${formattedMin}`);

            // Update active pill state
            document.querySelectorAll('.quick-pill').forEach(pill => {
                const pH = pill.getAttribute('data-hour');
                const pM = pill.getAttribute('data-mins');
                if (pH === hour && pM === formattedMin) {
                    pill.classList.add('active');
                } else {
                    pill.classList.remove('active');
                }
            });

            // Trigger Pop & Pulse Animations
            triggerUpdateAnimations();

            // Show temporary "Calculation updated!" badge
            if (recalcNotice) {
                recalcNotice.classList.remove('d-none');
                recalcNotice.classList.remove('badge-pop');
                void recalcNotice.offsetWidth; // trigger reflow
                recalcNotice.classList.add('badge-pop');
                setTimeout(() => {
                    recalcNotice.classList.add('d-none');
                }, 2800);
            }

            // Reset button to Success state briefly
            if (optimizeBtn) {
                btnIcon.className = "bi bi-check2-circle me-1";
                btnText.textContent = "Optimized!";
                setTimeout(() => {
                    btnIcon.className = "bi bi-lightning-charge-fill me-1";
                    btnText.textContent = "Optimize";
                    optimizeBtn.disabled = false;
                }, 700);
            }

        } catch (err) {
            alert(err.message);
            if (optimizeBtn) {
                btnIcon.className = "bi bi-lightning-charge-fill me-1";
                btnText.textContent = "Optimize";
                optimizeBtn.disabled = false;
            }
        } finally {
            targetCards.forEach(id => {
                const el = document.getElementById(id);
                if (el) el.classList.remove('is-calculating');
            });
        }
    }

    function updateDOMWithResults(data) {
        evaluation = data;

        // 1. Departure time text
        document.querySelectorAll('.dep-time-display').forEach(el => {
            el.textContent = data.departure_time;
        });

        // 2. Best Route Card
        const bestRouteDisplay = document.getElementById('bestRouteDisplay');
        if (bestRouteDisplay) bestRouteDisplay.textContent = data.best_route;

        const bestRouteText = document.getElementById('bestRouteText');
        if (bestRouteText) bestRouteText.textContent = data.best_route;

        const bestRouteGainText = document.getElementById('bestRouteGainText');
        if (bestRouteGainText) bestRouteGainText.textContent = data.best_route;

        const bestDurationFormattedDisplay = document.getElementById('bestDurationFormattedDisplay');
        if (bestDurationFormattedDisplay) bestDurationFormattedDisplay.textContent = data.best_duration_formatted;

        const bestArrivalDisplay = document.getElementById('bestArrivalDisplay');
        if (bestArrivalDisplay) bestArrivalDisplay.textContent = data.best_arrival_time;

        const maxTimeSavedDisplay = document.getElementById('maxTimeSavedDisplay');
        if (maxTimeSavedDisplay) maxTimeSavedDisplay.textContent = data.max_time_saved_formatted;

        const worstRouteDisplay = document.getElementById('worstRouteDisplay');
        if (worstRouteDisplay) worstRouteDisplay.textContent = data.worst_route;

        const avgTimeSavedFormattedDisplay = document.getElementById('avgTimeSavedFormattedDisplay');
        if (avgTimeSavedFormattedDisplay) avgTimeSavedFormattedDisplay.textContent = data.avg_time_saved_formatted;

        // 3. Savings Card
        const savingsBestRouteName = document.getElementById('savingsBestRouteName');
        if (savingsBestRouteName) savingsBestRouteName.textContent = data.best_route;

        const baselineWorstRoute = document.getElementById('baselineWorstRoute');
        if (baselineWorstRoute) baselineWorstRoute.textContent = data.worst_route;

        const baselineWorstDuration = document.getElementById('baselineWorstDuration');
        if (baselineWorstDuration) baselineWorstDuration.textContent = data.worst_duration_formatted;

        // Re-populate savings list (all times in hours and minutes, no decimals!)
        const savingsList = document.getElementById('savingsList');
        if (savingsList) {
            let html = '';
            data.routes.forEach(route => {
                if (!route.is_best) {
                    html += `
                    <div class="list-group-item px-0 py-3 border-bottom">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <span class="fw-bold text-dark fs-6">${route.route}</span>
                            <span class="badge bg-primary text-white fs-6 px-3 py-1 rounded-pill">
                                Save ${route.time_saved_formatted}
                            </span>
                        </div>
                        <div class="d-flex justify-content-between text-muted small">
                            <span>Alternative takes: <strong>${route.duration_formatted}</strong></span>
                            <span class="text-success fw-semibold">${Math.round(route.savings_percentage)}% faster</span>
                        </div>
                        <div class="progress mt-2" style="height: 6px;">
                            <div class="progress-bar bg-success" role="progressbar" style="width: ${100 - route.savings_percentage}%;"></div>
                            <div class="progress-bar bg-danger opacity-75" role="progressbar" style="width: ${route.savings_percentage}%;"></div>
                        </div>
                    </div>`;
                }
            });
            savingsList.innerHTML = html;
        }

        // 4. Comparison Table (Efficiency and Model Type removed, times in hours & minutes!)
        const tableBody = document.getElementById('routeTableBody');
        if (tableBody) {
            let tHtml = '';
            data.routes.forEach(r => {
                const trClass = r.is_best ? 'table-success-subtle fw-semibold row-sweep' : 'row-sweep';
                const routeBadge = r.is_best ? '<span class="route-badge best">' + r.route + '</span> <span class="badge bg-success text-white ms-1">Recommended</span>' : '<span class="route-badge">' + r.route + '</span>';
                const durDisplay = `<span class="fs-6 fw-bold ${r.is_best ? 'text-success' : 'text-dark'}">${r.duration_formatted}</span>`;
                const savedDisplay = r.is_best 
                    ? '<span class="text-success fw-bold"><i class="bi bi-check2-all me-1"></i>0m (Fastest)</span>'
                    : `<span class="text-danger fw-bold">+${r.time_saved_formatted}</span><span class="text-muted small d-block">(${Math.round(r.savings_percentage)}% slower)</span>`;

                tHtml += `
                <tr class="${trClass}">
                    <td class="ps-4">${routeBadge}</td>
                    <td>${durDisplay}</td>
                    <td><span class="text-dark">${r.arrival_time}</span></td>
                    <td>${savedDisplay}</td>
                </tr>`;
            });
            tableBody.innerHTML = tHtml;
        }

        // 5. Chart Time and Assignment link
        const chartTimeDisplay = document.getElementById('chartTimeDisplay');
        if (chartTimeDisplay) chartTimeDisplay.textContent = data.departure_time;

        const assignmentViewLink = document.getElementById('assignmentViewLink');
        if (assignmentViewLink) {
            assignmentViewLink.href = `/get_best_route?hour=${data.departure_hour}&mins=${data.departure_minute}`;
        }

        // 6. Update Bar Chart
        initBarChart(data);
    }

    function triggerUpdateAnimations() {
        const bestCard = document.getElementById('bestRouteCard');
        if (bestCard) {
            bestCard.classList.remove('pulse-animated', 'card-calculating-flash');
            void bestCard.offsetWidth; // trigger reflow
            bestCard.classList.add('pulse-animated', 'card-calculating-flash');
        }

        const elementsToPop = [
            'bestRouteDisplay',
            'bestDurationFormattedDisplay',
            'bestArrivalDisplay',
            'maxTimeSavedDisplay'
        ];
        elementsToPop.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.classList.remove('number-pop');
                void el.offsetWidth;
                el.classList.add('number-pop');
            }
        });
    }

    // Trigger initial entrance animation on page load
    triggerUpdateAnimations();

    // 3. Time input bounds validation helper
    if (minsInput) {
        minsInput.addEventListener('change', function () {
            let val = parseInt(this.value, 10);
            if (isNaN(val) || val < 0) this.value = "00";
            else if (val > 59) this.value = "59";
            else this.value = val < 10 ? '0' + val : val.toString();
        });
    }
});
