import driver from '../driver.js';

const querySingleResult = async (statement) => {
  const session = driver.session();

  let result;
  let error;

  try {
    const response = await session.run(statement);
    result = response.records[0].get(0);
  } catch (e) {
    error = e;
  } finally {
    await session.close();
  }

  if (error) {
    throw error;
  }

  return result;
};

export default querySingleResult;
