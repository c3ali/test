document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const refineBtn = document.getElementById('refine-btn');
    const descriptionInput = document.getElementById('project-description');
    const feedbackInput = document.getElementById('feedback-text');
    const statusArea = document.getElementById('status-area');
    const resultsArea = document.getElementById('results-area');
    const codeFilesContainer = document.getElementById('code-files');
    const projectIdDisplay = document.getElementById('project-id-display');

    let currentProjectId = null;

    // --- Génération initiale ---
    generateBtn.addEventListener('click', async () => {
        const description = descriptionInput.value.trim();
        if (!description) {
            alert('Veuillez entrer une description pour le projet.');
            return;
        }

        disableButtons(true);
        setStatus('Génération en cours... Veuillez patienter.');

        try {
            const response = await fetch('/generate_project_async', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ description: description }),
            });

            if (!response.ok) throw new Error('La requête de génération a échoué.');

            const data = await response.json();
            currentProjectId = data.project_id;
            projectIdDisplay.textContent = `ID: ${currentProjectId}`;

            setStatus(`Projet créé avec l'ID ${currentProjectId}. En attente des résultats...`);
            pollForResults(currentProjectId);

        } catch (error) {
            setStatus(`Erreur : ${error.message}`);
            disableButtons(false);
        }
    });

    // --- Raffinement ---
    refineBtn.addEventListener('click', async () => {
        const feedback = feedbackInput.value.trim();
        if (!feedback) {
            alert('Veuillez entrer votre demande de modification.');
            return;
        }

        disableButtons(true);
        setStatus(`Raffinement du projet ${currentProjectId} en cours...`);

        try {
            const response = await fetch(`/refine_project/${currentProjectId}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ feedback: feedback }),
            });

            if (!response.ok) throw new Error('La requête de raffinement a échoué.');

            const data = await response.json();
            setStatus(`Demande de raffinement acceptée. En attente des résultats...`);
            pollForResults(currentProjectId, true);

        } catch (error) {
            setStatus(`Erreur : ${error.message}`);
            disableButtons(false);
        }
    });


    // --- Fonctions utilitaires ---

    function pollForResults(projectId, isRefinement = false) {
        const interval = setInterval(async () => {
            try {
                const response = await fetch(`/project_status/${projectId}`);
                if (!response.ok) return; // Le serveur n'est peut-être pas encore prêt

                const project = await response.json();

                const expectedStatus = isRefinement ? "refined" : "completed";
                if (project.status === expectedStatus || project.status === "completed") {
                    clearInterval(interval);
                    setStatus('Projet généré avec succès !');
                    displayResults(project);
                    disableButtons(false);
                }
            } catch (error) {
                // Continue de poller
            }
        }, 3000); // Interroge toutes les 3 secondes
    }

    function displayResults(project) {
        resultsArea.classList.remove('hidden');
        codeFilesContainer.innerHTML = ''; // Nettoyer les anciens résultats

        for (const [filename, code] of Object.entries(project.code)) {
            const fileElement = document.createElement('div');
            fileElement.className = 'file';

            const header = document.createElement('div');
            header.className = 'file-header';
            header.textContent = filename;

            const content = document.createElement('pre');
            content.className = 'file-content';
            content.textContent = code;

            fileElement.appendChild(header);
            fileElement.appendChild(content);
            codeFilesContainer.appendChild(fileElement);
        }
    }

    function setStatus(message) {
        statusArea.textContent = message;
    }

    function disableButtons(disabled) {
        generateBtn.disabled = disabled;
        refineBtn.disabled = disabled;
    }
});
