document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const refineBtn = document.getElementById('refine-btn');
    const descriptionInput = document.getElementById('project-description');
    const feedbackInput = document.getElementById('feedback-text');
    const statusArea = document.getElementById('status-area');
    const resultsArea = document.getElementById('results-area');
    const codeFilesContainer = document.getElementById('code-files');
    const projectIdDisplay = document.getElementById('project-id-display');
    const githubRepoInput = document.getElementById('github-repo-name');
    const githubPrivateInput = document.getElementById('github-is-private');
    const githubLinkContainer = document.getElementById('github-link');

    let currentProjectId = null;

    // --- Génération initiale ---
    generateBtn.addEventListener('click', async () => {
        const description = descriptionInput.value.trim();
        if (!description) {
            alert('Veuillez entrer une description pour le projet.');
            return;
        }

        disableButtons(true);
        setStatus('Demande envoyée. Préparation de la génération...');

        let requestBody = { description: description };
        const repoName = githubRepoInput.value.trim();
        if (repoName) {
            requestBody.github_options = {
                repo_name: repoName,
                is_private: githubPrivateInput.checked
            };
        }

        try {
            const response = await fetch('/generate_project_async', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(requestBody),
            });

            if (!response.ok) throw new Error(`La requête a échoué avec le statut ${response.status}`);

            const data = await response.json();
            currentProjectId = data.project_id;
            projectIdDisplay.textContent = `ID: ${currentProjectId}`;

            setStatus(`Projet créé (ID: ${currentProjectId}). En attente des résultats...`);
            pollForResults(currentProjectId);

        } catch (error) {
            setStatus(`Erreur critique : ${error.message}`);
            disableButtons(false);
        }
    });

    // --- Raffinement ---
    refineBtn.addEventListener('click', async () => {
        // (La logique de raffinement reste inchangée pour l'instant)
    });

    // --- Fonctions utilitaires ---
    function pollForResults(projectId, isRefinement = false) {
        const interval = setInterval(async () => {
            try {
                const response = await fetch(`/project_status/${projectId}`);
                if (!response.ok) return;

                const project = await response.json();

                const expectedStatus = isRefinement ? "refined" : "completed";
                if (project.status === "completed" || project.status === "refined" || project.status === "failed") {
                    clearInterval(interval);
                    if (project.status === "failed") {
                        setStatus(`La génération a échoué. Erreur : ${project.error || 'Inconnue'}`);
                    } else {
                        setStatus('Projet généré et déployé avec succès !');
                        displayResults(project);
                    }
                    disableButtons(false);
                }
            } catch (error) {
                // Continue de poller
            }
        }, 5000); // Interroge toutes les 5 secondes
    }

    function displayResults(project) {
        resultsArea.classList.remove('hidden');
        codeFilesContainer.innerHTML = '';
        githubLinkContainer.innerHTML = '';

        // Afficher le lien GitHub
        if (project.github_url && !project.github_url.startsWith("Erreur")) {
            const link = document.createElement('a');
            link.href = project.github_url;
            link.target = '_blank';
            link.textContent = `Voir le projet sur GitHub : ${project.github_url}`;
            githubLinkContainer.appendChild(link);
        } else if (project.github_url) {
            githubLinkContainer.textContent = `Erreur GitHub : ${project.github_url}`;
        }

        // Afficher les fichiers
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
