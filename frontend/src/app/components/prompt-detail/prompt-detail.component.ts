import { Component, OnInit } from '@angular/core';
  import { ActivatedRoute, Router } from '@angular/router';
  import { PromptService, Prompt } from '../../services/prompt.service';

  @Component({
    selector: 'app-prompt-detail',
    templateUrl: './prompt-detail.component.html',
    styleUrls: ['./prompt-detail.component.css']
  })
  export class PromptDetailComponent implements OnInit {
    prompt: Prompt | null = null;
    loading = true;
    error = '';
    deleting = false;

    constructor(
      private route: ActivatedRoute,
      private router: Router,
      private promptService: PromptService
    ) {}

    ngOnInit(): void {
      const id = Number(this.route.snapshot.paramMap.get('id'));
      this.promptService.getPrompt(id).subscribe({
        next: (data) => {
          this.prompt = data;
          this.loading = false;
        },
        error: (err) => {
          this.error = err.status === 404 ? 'Prompt not found.' : 'Failed to load prompt.';
          this.loading = false;
        }
      });
    }

    deletePrompt(): void {
      if (!this.prompt || !confirm('Delete this prompt? This cannot be undone.')) return;
      this.deleting = true;
      this.promptService.deletePrompt(this.prompt.id).subscribe({
        next: () => this.router.navigate(['/prompts']),
        error: () => {
          this.error = 'Failed to delete prompt.';
          this.deleting = false;
        }
      });
    }

    complexityLevel(complexity: number): string {
      if (complexity <= 3) return 'low';
      if (complexity <= 7) return 'medium';
      return 'high';
    }

    formatDate(dateStr: string): string {
      return new Date(dateStr).toLocaleString('en-US', {
        year: 'numeric', month: 'long', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
      });
    }

    goBack(): void {
      this.router.navigate(['/prompts']);
    }
  }