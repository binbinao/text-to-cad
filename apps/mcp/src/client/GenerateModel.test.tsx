import { act, cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import GenerateModel, { generationPrompt } from './GenerateModel';

afterEach(cleanup);

describe('generationPrompt', () => {
  it('keeps the geometry request and required format in the agent prompt', () => {
    expect(generationPrompt(' A mounting bracket. ', '3mf')).toBe([
      'Create a CAD model with the installed CAD skill.',
      'Geometry request: A mounting bracket.',
      'Required output format: 3MF.',
      'Save the generated file and show it in CAD.',
    ].join('\n'));
  });
});

it('sends the selected format and geometry request', async () => {
  const send = vi.fn(async () => {});
  render(<GenerateModel send={send} />);
  fireEvent.change(screen.getByLabelText('Geometry request'), { target: { value: 'A 20 mm bearing block' } });
  fireEvent.click(screen.getByRole('radio', { name: 'GLB' }));
  await act(async () => { fireEvent.click(screen.getByRole('button', { name: 'Generate' })); });
  expect(send).toHaveBeenCalledWith(generationPrompt('A 20 mm bearing block', 'glb'));
  expect(screen.getByRole('status').textContent).toBe('Sent to agent');
});

it('keeps a failed delivery visible and does not claim the model was generated', async () => {
  const send = vi.fn(async () => { throw new Error('The chat closed.'); });
  render(<GenerateModel send={send} />);
  fireEvent.change(screen.getByLabelText('Geometry request'), { target: { value: 'A spur gear' } });
  await act(async () => { fireEvent.click(screen.getByRole('button', { name: 'Generate' })); });
  expect(screen.getByRole('alert').textContent).toBe('The chat closed.');
  expect(screen.queryByRole('status')).toBeNull();
});

it('queues where the host cannot send, instead of pretending generation started', async () => {
  const queue = vi.fn(async () => {});
  render(<GenerateModel queue={queue} />);
  fireEvent.change(screen.getByLabelText('Geometry request'), { target: { value: 'A finned heat sink' } });
  await act(async () => { fireEvent.click(screen.getByRole('button', { name: 'Add to chat' })); });
  expect(queue).toHaveBeenCalledWith(generationPrompt('A finned heat sink', 'step'));
  expect(screen.getByRole('status').textContent).toBe('Prompt added to chat');
});
