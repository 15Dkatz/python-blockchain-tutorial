import React, { useState } from 'react';
import { Button } from 'react-bootstrap';
import { MILLISECONDS_PY } from '../config';
import Transaction from './Transaction';

function ToggleTransactionDisplay({ block }) {
  const [displayTransaction, setDisplayTransaction] = useState(false);
  const { data } = block;

  const toggleDisplayTransaction = () => {
    setDisplayTransaction(!displayTransaction);
  }

  if (displayTransaction) {
    return (
      <div>
        {
          data.map(transaction => (
            <div key={transaction.id}>
              <hr />
              <Transaction transaction={transaction} />
            </div>
          ))
        }
        <br />
        <Button
          variant="danger"
          size="sm"
          onClick={toggleDisplayTransaction}
        >
          Show Less
        </Button>
      </div>
    )
  }

  return (
    <div>
      <br />
      <Button
        variant="danger"
        size="sm"
        onClick={toggleDisplayTransaction}
      >
        Show More
      </Button>
    </div>
  )
}

function Block({ block }) {
  const { timestamp, hash } = block;
  const hashDisplay = `${hash.substring(0, 15)}...`;
  const timestampDisplay = new Date(timestamp / MILLISECONDS_PY).toLocaleString();

  return (
    <div className="Block">
      <div>Hash: {hashDisplay}</div>
      <div>Timestamp: {timestampDisplay}</div>
      <ToggleTransactionDisplay block={block} />
    </div>
  )
}

export default Block;
