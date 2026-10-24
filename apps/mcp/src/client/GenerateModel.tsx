import { useState } from 'react';
import { Clipboard, Send } from 'lucide-react';
import { Button } from '@text-to-cad/ui/primitives/button';

export const CAD_FORMATS = [
  { id: 'step', label: 'STEP' },
  { id: 'stl', label: 'STL' },
  { id: '3mf', label: '3MF' },
  { id: 'glb', label: 'GLB' },
] as const;

export type CadFormat = typeof CAD_FORMATS[number]['id'];

export function generationPrompt(geometry: string, format: CadFormat): string {
  return [
    'Create a CAD model with the installed CAD skill.',
    `Geometry request: ${geometry.trim()}`,
    `Required output format: ${format.toUpperCase()}.`,
    'Save the generated file and show it in CAD.',
  ].join('\n');
}

const failure = (error: unknown) => error instanceof Error ? error.message : String(error);

/**
 * The CAD app's generator: a geometry request and its output format, sent to the agent that owns
 * the CAD skill. The viewer still only shows files; it never runs generated source.
 */
export default function GenerateModel({ send, queue, copy }: {
  send?(prompt: string): Promise<void>;
  queue?(prompt: string): Promise<void>;
  copy?(prompt: string): Promise<void>;
}) {
  const [geometry, setGeometry] = useState('');
  const [format, setFormat] = useState<CadFormat>('step');
  const [state, setState] = useState<{ busy: boolean; message: string; error?: true }>({ busy: false, message: '' });
  const trimmed = geometry.trim();
  const actionLabel = send ? 'Generate' : queue ? 'Add to chat' : 'Copy prompt';

  const submit = async () => {
    if (!trimmed || state.busy) return;
    const prompt = generationPrompt(trimmed, format);
    setState({ busy: true, message: 'Sending' });
    try {
      if (send) {
        await send(prompt);
        setState({ busy: false, message: 'Sent to agent' });
      } else if (queue) {
        await queue(prompt);
        setState({ busy: false, message: 'Prompt added to chat' });
      } else {
        if (!copy) throw new Error('No prompt destination is available.');
        await copy(prompt);
        setState({ busy: false, message: 'Prompt copied' });
      }
    } catch (error) {
      setState({ busy: false, message: failure(error), error: true });
    }
  };

  return <section className="cad-generator" aria-labelledby="cad-generator-heading">
    <h2 id="cad-generator-heading">Generate CAD geometry</h2>
    <form onSubmit={event => { event.preventDefault(); void submit(); }}>
      <label className="sr-only" htmlFor="cad-geometry">Geometry request</label>
      <textarea id="cad-geometry" value={geometry} onChange={event => setGeometry(event.target.value)}
        placeholder="A 40 x 20 x 6 mm mounting bracket with four 5 mm holes"
        rows={3} maxLength={4000} required disabled={state.busy} />
      <div className="cad-generator-controls">
        <fieldset>
          <legend>Output format</legend>
          <div role="radiogroup" aria-label="Output format">
            {CAD_FORMATS.map(option => <Button key={option.id} type="button" size="sm"
              variant={format === option.id ? 'default' : 'outline'} role="radio" aria-checked={format === option.id}
              onClick={() => setFormat(option.id)}>{option.label}</Button>)}
          </div>
        </fieldset>
        <Button type="submit" disabled={!trimmed || state.busy} aria-busy={state.busy}>
          {send ? <Send className={state.busy ? 'size-4 animate-pulse' : 'size-4'} aria-hidden="true" />
            : <Clipboard className="size-4" aria-hidden="true" />}
          {actionLabel}
        </Button>
      </div>
    </form>
    <p role={state.error ? 'alert' : 'status'} aria-live="polite" className={state.error ? 'text-destructive' : 'text-muted-foreground'}>{state.message}</p>
  </section>;
}
