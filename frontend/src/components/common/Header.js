import React from 'react';
import '../../assets/styles/header.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSignOutAlt } from '@fortawesome/free-solid-svg-icons';
import { useAuth } from '../../services/authService'; 

function Header() {
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    window.location.href = '/';
  };

  return (
    <header className="header">
      <div className="header-logo">
        <h2>AnnuairePolySécurisé</h2>
      </div>
      <nav className="header-nav">
        <ul>
          <li><a href="/">Annuaire</a></li>
          
          <li>
            <button onClick={handleLogout} className="logout-button" aria-label="Logout">
              <FontAwesomeIcon icon={faSignOutAlt} />
            </button>
          </li>
        </ul>
      </nav>
    </header>
  );
}

export default Header;
