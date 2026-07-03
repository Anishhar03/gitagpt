import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';

import { AuthScreen } from './AuthScreen';


it('submits the development display name', async () => {
  const user = userEvent.setup();
  const onDevLogin = vi.fn();
  render(<AuthScreen config={{ auth_mode: 'development' }} onDevLogin={onDevLogin} onGoogleLogin={() => {}} />);

  const input = screen.getByLabelText('Display name');
  await user.clear(input);
  await user.type(input, 'Anish');
  await user.click(screen.getByTitle('Continue'));

  expect(onDevLogin).toHaveBeenCalledWith('Anish');
});
