import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { PromptService } from '../../services/prompt.service';

@Component({
  selector: 'app-add-prompt',
  templateUrl: './add-prompt.component.html',
  styleUrls: ['./add-prompt.component.css']
})
export class AddPromptComponent {
  promptForm: FormGroup;
  submitting = false;
  submitError = '';

  constructor(
    private fb: FormBuilder,
    private promptService: PromptService,
    private router: Router
  ) {
    this.promptForm = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(3)]],
      content: ['', [Validators.required, Validators.minLength(20)]],
      complexity: [5, [Validators.required, Validators.min(1), Validators.max(10)]]
    });
  }

  get title() { return this.promptForm.get('title')!; }
  get content() { return this.promptForm.get('content')!; }
  get complexity() { return this.promptForm.get('complexity')!; }

  get contentLength(): number {
    return (this.content.value as string)?.length ?? 0;
  }

  complexityLevel(): string {
    const v = this.complexity.value as number;
    if (v <= 3) return 'low';
    if (v <= 7) return 'medium';
    return 'high';
  }

  onSubmit(): void {
    if (this.promptForm.invalid) {
      this.promptForm.markAllAsTouched();
      return;
    }
    this.submitting = true;
    this.submitError = '';

    this.promptService.createPrompt(this.promptForm.value).subscribe({
      next: (prompt) => {
        this.router.navigate(['/prompts', prompt.id]);
      },
      error: (err) => {
        this.submitting = false;
        if (err.error?.errors) {
          const errors = err.error.errors;
          if (errors['title'])      this.title.setErrors({ server: errors['title'] });
          if (errors['content'])    this.content.setErrors({ server: errors['content'] });
          if (errors['complexity']) this.complexity.setErrors({ server: errors['complexity'] });
        } else {
          this.submitError = 'Failed to create prompt. Please try again.';
        }
      }
    });
  }
}
