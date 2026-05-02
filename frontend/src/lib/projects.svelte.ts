import { apiRequest } from './api.svelte.ts';

export interface Project {
    id: number;
    name: string;
    created_by: number;
    created_at: string;
}

export interface Column {
    id: number;
    name: string;
    order: number;
    project_id: number;
}

class ProjectStore {
    projects = $state<Project[]>([]);
    currentProject = $state<Project | null>(null);
    columns = $state<Column[]>([]);
    isLoading = $state(false);

    async loadProjects() {
        this.isLoading = true;
        try {
            this.projects = await apiRequest('/projects');
            const savedId = localStorage.getItem('kanvia_current_project_id');
            if (savedId) {
                const savedProject = this.projects.find(p => p.id === parseInt(savedId));
                if (savedProject) {
                    this.setCurrentProject(savedProject);
                    return;
                }
            }
            if (this.projects.length > 0 && !this.currentProject) {
                this.setCurrentProject(this.projects[0]);
            }
        } catch (err) {
            console.error('Failed to load projects:', err);
        } finally {
            this.isLoading = false;
        }
    }

    setCurrentProject(project: Project) {
        this.currentProject = project;
        localStorage.setItem('kanvia_current_project_id', project.id.toString());
        this.loadColumns(project.id);
    }

    async loadColumns(projectId: number) {
        try {
            this.columns = await apiRequest(`/projects/${projectId}/columns`);
        } catch (err) {
            console.error('Failed to load columns:', err);
        }
    }

    async createColumn(name: string) {
        if (!this.currentProject) return;
        try {
            const doneCol = this.columns.find(c => c.name.toLowerCase() === 'done');
            const order = doneCol ? doneCol.order : this.columns.length;
            
            const newColumn = await apiRequest(`/projects/${this.currentProject.id}/columns`, 'POST', {
                name,
                order
            });
            
            await this.loadColumns(this.currentProject.id);
            return newColumn;
        } catch (err: any) {
            throw new Error(err.message);
        }
    }

    async createProject(name: string) {
        try {
            const newProject = await apiRequest('/projects', 'POST', { name });
            this.projects = [...this.projects, newProject];
            return newProject;
        } catch (err: any) {
            throw new Error(err.message);
        }
    }
}

export const projectStore = new ProjectStore();
