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

    if (sessionData.status === 'logged_in') {
         
        // const hasAnsweredAllQuestions = sessionData.user.answers.length > 0;
        // console.log('Has answered all questions:', hasAnsweredAllQuestions);

      if (window.location.pathname !== '/questions') {
        // If logged in and on the home page, redirect to questions

        const hasAnsweredAllQuestions = sessionData.user.answers.length > 0;
        console.log('Has answered all questions:', hasAnsweredAllQuestions);

        if(hasAnsweredAllQuestions != true){
        window.location.href = '/questions';
      }
    }
 
    }else{
      if (window.location.pathname !== '/') {
        window.location.href = '/';
      }
    }
  } catch (error) {
    // Not logged in or error occurred — do nothing
    console.warn('Auth check:', error.message);
  }
})();
