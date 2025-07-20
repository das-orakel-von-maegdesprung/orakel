(async () => {
  try {
    const response = await fetch('/session', {
      method: 'GET',
      credentials: 'include', // include cookies if session is stored that way
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) throw new Error('Session check failed');

    const data = await response.json();

    if (data.status === 'logged_in') {
      window.location.href = '/questions';
    }
  } catch (error) {
    // Not logged in or error occurred — do nothing
    console.warn('Auth check:', error.message);
  }
})();
