import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../assets/styles/Login.css';
import 'react-toastify/dist/ReactToastify.css';
import { toast } from 'react-toastify';


function Signup() {
  const [userData, setUserData] = useState({
    username: '',
    password: '',
    first_name: '',
    last_name: '',
    adresse: '',
    num_phone: ''
  });
  const navigate = useNavigate();

  const handlelogin=()=>{
    navigate('/login');
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/users`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      });
      toast(response.message)
      if (response.ok) {
        // Redirection après inscription réussie
        navigate('/login');
      } else {
        // Gérer les erreurs de l'API
        const errorData = await response.json();
        alert('Erreur lors de l\'inscription: ' + errorData.message);
      }
    } catch (error) {
      console.error('Erreur d\'inscription:', error);
      alert('Erreur lors de l\'inscription');
    }
  };

  const handleChange = (e) => {
    setUserData({
      ...userData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          name="username"
          placeholder="Nom d'utilisateur"
          value={userData.username}
          onChange={handleChange}
          required
        />
        <input
          type="password"
          name="password"
          placeholder="Mot de passe"
          value={userData.password}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="first_name"
          placeholder="Prénom"
          value={userData.first_name}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="last_name"
          placeholder="Nom"
          value={userData.last_name}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="adresse"
          placeholder="Adresse"
          value={userData.adresse}
          onChange={handleChange}
          required
        />
        <input
          type="tel"
          name="num_phone"
          placeholder="Numéro de téléphone"
          value={userData.num_phone}
          onChange={handleChange}
          required
        />
        <button type="submit">S'inscrire</button>
      </form>
      <p><a className="link" onClick={handlelogin}>Se connecter</a></p>
    </div>
  );
}

export default Signup;