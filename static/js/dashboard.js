async function refreshStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();

        document.getElementById('ping-val').innerText = data.ping;
        const container = document.getElementById('dashboard-grid');

        container.innerHTML = data.stacks.map(stack => {
            const isAllRunning = stack.running === stack.count;
            return `
                <div class="bg-[#161b22] border border-white/10 p-7 rounded-[2.5rem] shadow-lg transition-transform hover:scale-[1.02]">
                    <h3 class="text-xl font-bold text-white uppercase mb-4">${stack.name}</h3>
                    <div class="grid grid-cols-2 gap-4 pt-4 border-t border-white/5 font-mono">
                        <div><p class="text-[9px] opacity-40 uppercase">Instancje</p><p class="text-lg font-bold">${stack.count}</p></div>
                        <div class="${isAllRunning ? 'text-blue-400' : 'text-red-500'}">
                            <p class="text-[9px] opacity-40 uppercase">Aktywne</p>
                            <p class="text-lg font-bold">${stack.running}</p>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    } catch (e) {
        console.error("Dashboard refresh error:", e);
    }
}

// Start odświeżania co 3 sekundy
refreshStats();
setInterval(refreshStats, 3000);