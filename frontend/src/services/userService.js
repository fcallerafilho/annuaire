export const fetchUsers = async (searchTerm = '') => {
  const token = localStorage.getItem('token');
  
  const response = await fetch(`${process.env.REACT_APP_API_URL}/users${searchTerm ? `?search=${searchTerm}` : ''}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
      throw new Error('Session expirée');
    }
    throw new Error('Erreur lors du chargement des contacts');
  }

  return response.json();
};

export const createUser = async (userData) => {
  const token = localStorage.getItem('token');
  
  try {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/users`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(userData)
    });

    const data = await response.json();
    
    if (!response.ok) {
      console.error('Erreur serveur:', data);
      
      if (response.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login';
        throw new Error('Session expirée');
      }
      
      throw new Error(data.message || 'Erreur lors de la création de l\'utilisateur');
    }

    return data;
  } catch (error) {
    console.error('Erreur complète:', error);
    throw error;
  }
};
export const promoteUser = async (userId) => {
  const token = localStorage.getItem('token');
  
  const response = await fetch(`${process.env.REACT_APP_API_URL}/users/${userId}/promote`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    throw new Error('Erreur lors de la promotion de l\'utilisateur');
  }

  return response.json();
};

export const demoteUser = async (userId) => {
  const token = localStorage.getItem('token');
  
  const response = await fetch(`${process.env.REACT_APP_API_URL}/users/${userId}/demote`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    throw new Error('Erreur lors de la rétrogradation de l\'utilisateur');
  }

  return response.json();
};

export const deleteUser = async (userId) => {
  const token = localStorage.getItem('token');
  
  const response = await fetch(`${process.env.REACT_APP_API_URL}/users/${userId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    throw new Error('Erreur lors de la suppression de l\'utilisateur');
  }

  return response.json();
};
export const changePassword = async (userId, oldPassword, newPassword) => {
  const token = localStorage.getItem('token');
  
  const response = await fetch(`${process.env.REACT_APP_API_URL}/users/${userId}/password`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      old_password: oldPassword,
      new_password: newPassword
    })
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.message || 'Erreur lors du changement de mot de passe');
  }

  return response.json();
};