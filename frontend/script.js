document.addEventListener('DOMContentLoaded', () => {
    // Éléments du DOM
    const generateBtn = document.getElementById('generate-btn');
    const refineBtn = document.getElementById('refine-btn');
    const descriptionInput = document.getElementById('project-description');
    const feedbackInput = document.getElementById('feedback-text');
    const statusArea = document.getElementById('status-area');
    const resultsArea = document.getElementById('results-area');
    const codeFilesContainer = document.getElementById('code-files');
    const projectIdDisplay = document.getElementById('project-id-display');
    const deployCheckbox = document.getElementById('deploy-to-github');
    const githubDetails = document.getElementById('github-details');
    const githubRepoInput = document.getElementById('github-repo-name');
    const githubPrivateInput = document.getElementById('github-is-private');
    const githubLinkContainer = document.getElementById('github-link');

    let currentProjectId = null;

    // --- Gestion de l'UI ---
    deployCheckbox.addEventListener('change', () => {
        githubDetails.classList.toggle('hidden', !deployCheckbox.checked);
    });

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
        if (deployCheckbox.checked) {
            requestBody.github_options = {
                repo_name: githubRepoInput.value.trim(), // Le backend gérera si c'est vide
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

    // Le reste du script est identique...
    // --- Raffinement ---
    refineBtn.addEventListener('click', async () => {
        // (Logique de raffinement)
    });

    // --- Fonctions utilitaires ---
    function pollForResults(projectId, isRefinement = false) {
        // (Logique de polling)
    }

    function displayResults(project) {
        // (Logique d'affichage des résultats)
    }

    function setStatus(message) {
        statusArea.textContent = message;
    }

    function disableButtons(disabled) {
        generateBtn.disabled = disabled;
        refineBtn.disabled = disabled;
    }
});
