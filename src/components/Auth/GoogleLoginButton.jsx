import React, { useEffect, useRef } from 'react';
import { useAuth } from '../../hooks/useAuth';

const GoogleLoginButton = () => {
  const { user, signOut } = useAuth();
  const divRef = useRef(null);

  useEffect(() => {
    if (window.google && divRef.current && !user) {
      window.google.accounts.id.renderButton(divRef.current, {
        theme: 'outline',
        size: 'large',
        type: 'standard',
      });
    }
  }, [user]);

  if (user) {
    return (
      <div className="flex items-center space-x-4">
        <img
          src={user.picture}
          alt={user.name}
          className="w-10 h-10 rounded-full"
        />
        <span className="font-medium">{user.name}</span>
        <button
          onClick={signOut}
          className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
        >
          Sign Out
        </button>
      </div>
    );
  }

  return <div ref={divRef}></div>;
};

export default GoogleLoginButton;
