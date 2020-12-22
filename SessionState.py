Skip to content
 
Search…
All gists
Back to GitHub
@Frenz86 
@tvst
tvst/SessionState.py
Last active 25 days ago • Report abuse
48
7
 Code
 Revisions 11
 Stars 48
 Forks 7
<script src="https://gist.github.com/tvst/036da038ab3e999a64497f42de966a92.js"></script>
A possible design for doing per-session persistent state in Streamlit
SessionState.py
"""Hack to add per-session state to Streamlit.
Usage
-----
>>> import SessionState
>>>
>>> session_state = SessionState.get(user_name='', favorite_color='black')
>>> session_state.user_name
''
>>> session_state.user_name = 'Mary'
>>> session_state.favorite_color
'black'
Since you set user_name above, next time your script runs this will be the
result:
>>> session_state = get(user_name='', favorite_color='black')
>>> session_state.user_name
'Mary'
"""
try:
    import streamlit.ReportThread as ReportThread
    from streamlit.server.Server import Server
except Exception:
    # Streamlit >= 0.65.0
    import streamlit.report_thread as ReportThread
    from streamlit.server.server import Server


class SessionState(object):
    def __init__(self, **kwargs):
        """A new SessionState object.
        Parameters
        ----------
        **kwargs : any
            Default values for the session state.
        Example
        -------
        >>> session_state = SessionState(user_name='', favorite_color='black')
        >>> session_state.user_name = 'Mary'
        ''
        >>> session_state.favorite_color
        'black'
        """
        for key, val in kwargs.items():
            setattr(self, key, val)


def get(**kwargs):
    """Gets a SessionState object for the current session.
    Creates a new object if necessary.
    Parameters
    ----------
    **kwargs : any
        Default values you want to add to the session state, if we're creating a
        new one.
    Example
    -------
    >>> session_state = get(user_name='', favorite_color='black')
    >>> session_state.user_name
    ''
    >>> session_state.user_name = 'Mary'
    >>> session_state.favorite_color
    'black'
    Since you set user_name above, next time your script runs this will be the
    result:
    >>> session_state = get(user_name='', favorite_color='black')
    >>> session_state.user_name
    'Mary'
    """
    # Hack to get the session object from Streamlit.

    ctx = ReportThread.get_report_ctx()

    this_session = None

    current_server = Server.get_current()
    if hasattr(current_server, '_session_infos'):
        # Streamlit < 0.56
        session_infos = Server.get_current()._session_infos.values()
    else:
        session_infos = Server.get_current()._session_info_by_id.values()

    for session_info in session_infos:
        s = session_info.session
        if (
            # Streamlit < 0.54.0
            (hasattr(s, '_main_dg') and s._main_dg == ctx.main_dg)
            or
            # Streamlit >= 0.54.0
            (not hasattr(s, '_main_dg') and s.enqueue == ctx.enqueue)
            or
            # Streamlit >= 0.65.2
            (not hasattr(s, '_main_dg') and s._uploaded_file_mgr == ctx.uploaded_file_mgr)
        ):
            this_session = s

    if this_session is None:
        raise RuntimeError(
            "Oh noes. Couldn't get your Streamlit Session object. "
            'Are you doing something fancy with threads?')

    # Got the session object! Now let's attach some state into it.

    if not hasattr(this_session, '_custom_session_state'):
        this_session._custom_session_state = SessionState(**kwargs)

    return this_session._custom_session_state
@treuille
treuille commented on 24 Oct 2019
I would add

__all__ = ['get'] 
to the end of this.

@Codeguyross
Codeguyross commented on 27 Jul
I would add

__all__ = ['get'] 
to the end of this.

Im a little new here and trying to understand. What do you mean by add __all__ = ['get'] to the end? Can you provide an example and explain why? Thanks!

@wtfzambo
wtfzambo commented on 27 Jul
This is lovely! I have dynamic sliders in my app (meaning that they change based on a certain user input), and I used this solution to preserve slider values!

@benlindsay
benlindsay commented on 4 Aug
For anyone running into errors with this in what are currently nightly release versions, making these changes should fix it:

from streamlit.server.Server import Server
should change to

from streamlit.server.server import Server
and

import streamlit.ReportThread as ReportThread
should change to

import streamlit.report_thread as ReportThread
@gremloon
gremloon commented on 14 Aug • 
I tried to upgrade to 0.65.1 and run streamlit. When trying to work with the posted SessionState.py i just keep running into:

RuntimeError: Oh noes. Couldn't get your Streamlit Session objectAre you doing something fancy with threads?

this_session keeps coming up as None.

Even in the simplest scenario:

import streamlit as st
import st_state_patchv2
test = st_state_patchv2.get()
I cleand out all streamlit install in virtual envs or on system level and did a clean install of 0.65.1 including a force-reinstall with pip.

I also installed in Docker to make sure of clean environment
streamlit-nightly==0.64.1.dev20200805 -> worked
streamlit==0.65.1 -> failed

Any ideas?

@gremloon
gremloon commented on 15 Aug
It seems like this logic doesnt work anymore with the newest version:

if (
            # Streamlit < 0.54.0
            (hasattr(s, '_main_dg') and s._main_dg == ctx.main_dg)
            or
            # Streamlit >= 0.54.0
            (not hasattr(s, '_main_dg') and s.enqueue == ctx.enqueue)
        ):
            this_session = s
Seems like one now just has to compare on the actual ids in session_info / ctx to get the current session_id of the thread?

for session_info in session_infos:
        s = session_info.session
        if s.id == ctx.session_id:
            this_session = s
@okld
okld commented on 16 Aug
Even quicker if you don't plan to use Streamlit < 0.56, instead of looping through session infos, there's a private method retrieving the correct session_info object based on the report thread's session id. I've been using the following snippet for some time, and it worked before and after 0.65 update.

def _get_session():
    session_id = get_report_ctx().session_id
    session_info = Server.get_current()._get_session_info(session_id)

    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")
    
    return session_info.session
@andreaschiappacasse
andreaschiappacasse commented on 20 Aug
Even quicker if you don't plan to use Streamlit < 0.56, instead of looping through session infos, there's a private method retrieving the correct session_info object based on the report thread's session id. I've been using the following snippet for some time, and it worked before and after 0.65 update.

def _get_session():
    session_id = get_report_ctx().session_id
    session_info = Server.get_current()._get_session_info(session_id)

    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")
    
    return session_info.session
Thanks @Ghasel, this works fine in my case, while the current method based on this comparison:

(not hasattr(s, '_main_dg') and s._uploaded_file_mgr == ctx.uploaded_file_mgr)
was not working with Streamlit -0.65.2, causing the same state to be retrieved from different sessions with cross-talk issues.

@benlindsay
benlindsay commented on 7 Sep • 
Is there an updated version of this for 0.66.0? I'm seeing this error:

image

Here are the import statements in my SessionState.py:

import streamlit.report_thread as ReportThread
from streamlit.server.server import Server
and my app just looks like this:

import SessionState
import streamlit as st

session = SessionState.get(a=5)

st.write(session.a)
Ignore all this, I didn't catch the updates in the gist itself. Those updates fix it. Thanks all!

@FranzDiebold
FranzDiebold commented on 9 Sep
Thanks @tvst for this nice piece of code 👍 and @Ghasel for the code snippet 👏!
With the original code I had problems with interfering sessions, so I forked this Gist to work with Streamlit >= 0.65:

https://gist.github.com/FranzDiebold/898396a6be785d9b5ca6f3706ef9b0bc

@jparkhill
jparkhill commented on 21 Sep
I wish this would just make it into a stable API already :P

@AviSoori1x
AviSoori1x commented on 6 Oct • 
Awesome work and thank you for implementing this!
Just to verify, if I create a multi-user streamlit app running on a server with several users using it concurrently, will the session state be unique to each user? I have gotten it to work in my test environment but I'm not sure what needs to change in production
I know that the session state is supposed to be unique to the browser session but when I access the same app running on localhost using two browser windows concurrently(different browsers), one stream of data precessing gets entangled in the other, which would be an issue in production.

@ryshoooo
ryshoooo commented on 10 Oct • 
I was having trouble using this implementation to get the correct session. I have a simple login/logout need for the streamlit dashboard with multiple users. While using the SessionState to remember which user is logged in, the session was always incorrectly identified and the login user was always overwritten by the latest logged user. Which was pretty problematic.

I solved it by using st.cache on the context session id. If anyone is interested, this is my SessionState.py; the interface works the exact same way (i.e. SessionState.get(variable_name=variable_value)), but this at least does not interfere with other users using the dashboard.

from streamlit.report_thread import get_report_ctx
import streamlit as st


class SessionState(object):
    def __init__(self, **kwargs):
        """A new SessionState object.

        Parameters
        ----------
        **kwargs : any
            Default values for the session state.

        Example
        -------
        >>> session_state = SessionState(user_name='', favorite_color='black')
        >>> session_state.user_name = 'Mary'
        ''
        >>> session_state.favorite_color
        'black'

        """
        for key, val in kwargs.items():
            setattr(self, key, val)


@st.cache(allow_output_mutation=True)
def get_session(id, **kwargs):
    return SessionState(**kwargs)


def get(**kwargs):
    """Gets a SessionState object for the current session.

    Creates a new object if necessary.

    Parameters
    ----------
    **kwargs : any
        Default values you want to add to the session state, if we're creating a
        new one.

    Example
    -------
    >>> session_state = get(user_name='', favorite_color='black')
    >>> session_state.user_name
    ''
    >>> session_state.user_name = 'Mary'
    >>> session_state.favorite_color
    'black'

    Since you set user_name above, next time your script runs this will be the
    result:
    >>> session_state = get(user_name='', favorite_color='black')
    >>> session_state.user_name
    'Mary'

    """
    ctx = get_report_ctx()
    id = ctx.session_id
    return get_session(id, **kwargs)
The main drawback of this method is in case the cache is cleared, the state is lost completely. So it's not great but at least works for different users just fine.

@AviSoori1x
AviSoori1x commented on 12 Oct
I lost track of this thread a while ago, but I think I managed to get session state to do the trick for me using FranzDiebold's alternative implementation. Will update once I get this finally running on a server.

@tvst
Owner
Author
tvst commented on 10 Nov
I wish this would just make it into a stable API already :P

We're working on it right now, actually! There are a few more details we need to nail down, plus a lot of testing, so my guess is we're looking at a January release.

@papagala
papagala commented on 11 Nov
@tvst this is incredible. I know this is not yet production ready, but I'm having trouble explaining why this works to my colleagues. Could you please explain how/why this works at least on a high level?

Thanks in advance.

@Frenz86
 
Leave a comment
Nessun file selezionato
Attach files by dragging & dropping, selecting or pasting them.
© 2020 GitHub, Inc.
Terms
Privacy
Security
Status
Help
Contact GitHub
Pricing
API
Training
Blog
About
