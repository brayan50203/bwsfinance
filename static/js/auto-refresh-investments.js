// Auto-refresh de investimentos
let autoRefreshInterval = null;
let isUpdating = false;

async function updateInvestments(silent = false) {
    if (isUpdating) return;
    
    const btn = document.getElementById('updateInvestmentsBtn');
    if (!btn) return;
    
    isUpdating = true;
    const originalContent = btn.innerHTML;

    if (!silent) {
        btn.innerHTML = '⏳';
        btn.disabled = true;
    }

    try {
        const response = await fetch('/investments/update-quotes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (data.success || data.updated !== undefined) {
            if (!silent) {
                btn.innerHTML = '✅';
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                // Atualiza silenciosamente em background
                console.log('🔄 Investimentos atualizados:', data.updated || 0);
                location.reload();
            }
        } else {
            if (!silent) {
                alert('Erro ao atualizar investimentos: ' + (data.error || 'Erro desconhecido'));
            }
            btn.innerHTML = originalContent;
            btn.disabled = false;
        }
    } catch (error) {
        console.error('Erro ao atualizar investimentos:', error);
        if (!silent) {
            alert('Erro ao atualizar investimentos. Verifique o console.');
        }
        btn.innerHTML = originalContent;
        btn.disabled = false;
    } finally {
        isUpdating = false;
    }
}

function startAutoRefresh() {
    // Limpar interval existente
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    // Atualizar a cada 5 minutos (300000ms) silenciosamente
    autoRefreshInterval = setInterval(() => {
        console.log('🔄 Auto-atualizando investimentos...');
        updateInvestments(true); // true = silent mode
    }, 300000);
    
    console.log('✅ Auto-refresh ativado (5 minutos)');
}

// Iniciar quando a página carregar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startAutoRefresh);
} else {
    startAutoRefresh();
}

// Limpar ao sair
window.addEventListener('beforeunload', () => {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
});
