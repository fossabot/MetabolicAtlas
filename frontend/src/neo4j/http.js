import axios from 'axios';

const postStatement = async (statement) => {
  const url = 'http://localhost:7474/db/neo4j/tx ';
  const payload = {
    statements: [{ statement }],
  };

  return axios.post(url, payload);
};

export default postStatement;
