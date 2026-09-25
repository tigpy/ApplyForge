import { describe, it, expect, vi } from 'vitest';
import { api, API_BASE } from './api';

describe('ApplyForge Web API Client', () => {
  it('should have a default API base URL', () => {
    expect(API_BASE).toBeDefined();
    expect(typeof API_BASE).toBe('string');
  });

  it('should fetch candidate profile', async () => {
    const mockProfile = { id: 1, name: 'Aryan Singh', email: 'aryan@example.com' };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockProfile,
    } as any);

    const result = await api.getCandidate();
    expect(result).toEqual(mockProfile);
    expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining('/candidate/profile'));
  });

  it('should approve an application with notes', async () => {
    const mockApp = { id: 10, status: 'APPROVED' };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockApp,
    } as any);

    const result = await api.approveApplication(10, 'Approved for security role');
    expect(result.status).toBe('APPROVED');
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/applications/10/approve'),
      expect.objectContaining({ method: 'POST' })
    );
  });
});
