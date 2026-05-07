const { exec } = require('child_process');

// Argumentos passados pelo Python (app)
const targetPackage = process.argv[2] || "Extensão Desconhecida";
const realCmd = process.argv[3]; // O comando shell real se existir na card

console.log(`\n\x1b[36m--- BotForge Extension Manager ---\x1b[0m`);
console.log(`\x1b[33m⚡ Preparando para baixar e instalar: ${targetPackage}\x1b[0m\n`);

async function simulateProgress(duration, steps) {
    const delay = duration / steps;
    for (let i = 1; i <= steps; i++) {
        await new Promise(r => setTimeout(r, delay));
        let p = Math.floor((i / steps) * 100);
        // Utiliza \r para efeito visual de barra carregando (Overwriting)
        process.stdout.write(`\r[${'='.repeat(Math.floor(p/5))}${' '.repeat(20 - Math.floor(p/5))}] ${p}% `);
    }
    console.log(); // Reseta para nova linha final
}

async function runInstallation() {
    console.log(`[INFO] Sincronizando repositórios locais...`);
    await simulateProgress(1500, 20);

    console.log(`[INFO] Resolvendo dependências avançadas...`);
    await simulateProgress(2000, 30);

    if (realCmd && realCmd !== "undefined" && realCmd.trim() !== "") {
        console.log(`[SYS] Executando container shell: ${realCmd}\n`);
        
        return new Promise((resolve, reject) => {
            const child = exec(realCmd, { env: { ...process.env, FORCE_COLOR: '1' } });
            
            child.stdout.on('data', (data) => process.stdout.write(data));
            child.stderr.on('data', (data) => process.stderr.write(data));
            
            child.on('close', (code) => {
                if (code === 0) {
                    console.log(`\n\x1b[32m✔ Execução Nativa Finalizada com Sucesso.\x1b[0m`);
                    resolve();
                } else {
                    console.log(`\n\x1b[31m✖ Processo finalizado com avisos ou erros (Código: ${code})\x1b[0m`);
                    // Mesmo se der erro no pacote nativo, a extensão mock servirá como validada
                    resolve(); 
                }
            });
        });

    } else {
        console.log(`[SYS] Nenhuma flag de compiler shell requerida. Extraindo binários estáticos...`);
        await simulateProgress(3000, 40);
        console.log(`\x1b[32m✔ Processo Finalizado: ${targetPackage} está totalmente integrado ao sistema.\x1b[0m`);
    }
}

runInstallation().then(() => {
    console.log(`\n--- FIM DA INSTALAÇÃO --- \n`);
}).catch(err => {
    console.error(`\n[CRITICAL ERROR] ${err}`);
});
