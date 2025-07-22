(async () => {
  try {
    const response = await fetch('/session-data', {
      method: 'GET',
      credentials: 'include', // include cookies if session is stored that way
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) throw new Error('Session check failed');

    const sessionData = await response.json();
    console.log('Auth check:', sessionData);

 
      const path = window.location.pathname;
 const hasAnsweredAllQuestions = sessionData.user.answers.length > 0;

   if (sessionData.status === 'logged_in') {



      switch (path) {
        case '/':
          if (!hasAnsweredAllQuestions) {
            window.location.href = '/questions';
          }else{
            window.location.href = '/chat';
          }
          break;
        case '/questions':
          if (hasAnsweredAllQuestions) {
            window.location.href = '/chat';
          }
          break;
        }
 
    }else{
      if (path !== '/') {
        window.location.href = '/';
      }
    }
  } catch (error) {
    // Not logged in or error occurred — do nothing
    console.warn('Auth check:', error.message);
  }
})();
